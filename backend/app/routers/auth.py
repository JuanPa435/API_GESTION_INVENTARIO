from datetime import timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
import logging
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..auth import security
from ..db import models, schemas, database
from ..auth.dependencies import get_current_active_user
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(database.get_db)
):
    # Permitir login con username o email usando el mismo campo 'username' del formulario OAuth2
    user = db.query(models.User).filter(
        or_(
            models.User.username == form_data.username,
            models.User.email == form_data.username,
        )
    ).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Build company_ids list from association table
    company_links = db.query(models.UserCompany).filter(models.UserCompany.user_id == user.id).all()
    company_ids = [link.company_id for link in company_links]

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": user.username,
        "company_ids": company_ids,
    }
    # Incluir company_id de conveniencia (primera empresa) si existe
    if company_ids:
        token_data["company_id"] = company_ids[0]
    access_token = security.create_access_token(data=token_data, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}


# Registro público de usuarios (sin autenticación previa)
class RegisterPayload(BaseModel):
    email: EmailStr
    username: str
    password: str


@router.post("/api/register", response_model=schemas.User, status_code=201)
async def public_register_user(request: Request, db: Session = Depends(database.get_db)):
    """Registro público: acepta JSON y también formularios.
    Evitamos validación previa de FastAPI para no responder 422 antes de tiempo.
    """
    content_type = request.headers.get("content-type", "").lower()
    data = None
    if "application/json" in content_type:
        try:
            data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        data = {
            "email": form.get("email"),
            "username": form.get("username"),
            "password": form.get("password"),
        }
    else:
        # Intento final: tratar de leer JSON, si no, error
        try:
            data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Unsupported Content-Type")

    # Validación con Pydantic
    try:
        payload = RegisterPayload(**(data or {}))
    except Exception:
        raise HTTPException(status_code=400, detail="Missing or invalid fields: required email, username, password")
    # Validar duplicados por email/username
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    username = payload.username
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    try:
        hashed_password = security.get_password_hash(payload.password)
        db_user = models.User(
            email=payload.email,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        logger.exception("Register failed")
        raise HTTPException(status_code=500, detail=f"Register failed: {e.__class__.__name__}")