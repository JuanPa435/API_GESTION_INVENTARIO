from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, distinct

from ..db import models, schemas, database
from ..auth.dependencies import get_current_active_user
from ..auth import security
from pydantic import BaseModel, EmailStr

router = APIRouter()

@router.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Solo usuarios que sean admin en alguna empresa pueden crear usuarios (si se usa este endpoint)
    has_admin = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id, models.UserCompany.role == 'admin').first()
    if not has_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        **user.dict(exclude={"password"}),
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Si el usuario es admin en alguna empresa, puede ver todos; si no, solo usuarios que compartan alguna empresa con él
    has_admin = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id, models.UserCompany.role == 'admin').first()
    if has_admin:
        users = db.query(models.User).offset(skip).limit(limit).all()
    else:
        my_company_ids = [c.company_id for c in db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id).all()]
        if not my_company_ids:
            return []
        users = (
            db.query(models.User)
            .join(models.UserCompany, models.User.id == models.UserCompany.user_id)
            .filter(models.UserCompany.company_id.in_(my_company_ids))
            .distinct()
            .offset(skip)
            .limit(limit)
            .all()
        )
    return users

@router.get("/users/my-company", response_model=List[schemas.User])
def read_users_my_company(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Lista los usuarios de una empresa del usuario autenticado.
    Usamos la primera membresía del usuario como contexto por defecto.
    """
    first_link = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id).first()
    if not first_link:
        raise HTTPException(status_code=400, detail="User is not member of any company")
    users = (
        db.query(models.User)
        .join(models.UserCompany, models.User.id == models.UserCompany.user_id)
        .filter(models.UserCompany.company_id == first_link.company_id)
        .distinct()
        .all()
    )
    return users


class UserWithRole(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str


@router.get("/users/my-company-detailed", response_model=List[UserWithRole])
def read_users_my_company_detailed(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Lista los usuarios de la empresa del usuario autenticado, incluyendo el rol de cada uno.
    Usa la primera membresía del usuario como contexto por defecto.
    """
    first_link = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id).first()
    if not first_link:
        raise HTTPException(status_code=400, detail="User is not member of any company")
    rows = (
        db.query(
            models.User.id,
            models.User.username,
            models.User.email,
            models.UserCompany.role,
        )
        .join(models.UserCompany, models.User.id == models.UserCompany.user_id)
        .filter(models.UserCompany.company_id == first_link.company_id)
        .all()
    )
    result = [UserWithRole(id=r[0], username=r[1], email=r[2], role=r[3] or 'employee') for r in rows]
    return result


@router.get("/users/company/{company_id}/detailed", response_model=List[UserWithRole])
def read_users_company_detailed(
    company_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Lista usuarios (con rol) de la compañía indicada.
    Requiere que el usuario autenticado sea admin en esa compañía.
    """
    admin_link = db.query(models.UserCompany).filter(
        models.UserCompany.user_id == current_user.id,
        models.UserCompany.company_id == company_id,
        models.UserCompany.role == 'admin'
    ).first()
    if not admin_link:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    rows = (
        db.query(
            models.User.id,
            models.User.username,
            models.User.email,
            models.UserCompany.role,
        )
        .join(models.UserCompany, models.User.id == models.UserCompany.user_id)
        .filter(models.UserCompany.company_id == company_id)
        .all()
    )
    return [UserWithRole(id=r[0], username=r[1], email=r[2], role=r[3] or 'employee') for r in rows]

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    has_admin = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id, models.UserCompany.role == 'admin').first()
    if not has_admin:
        my_company_ids = [c.company_id for c in db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id).all()]
        if not my_company_ids:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        shared = db.query(models.UserCompany).filter(models.UserCompany.user_id == user.id, models.UserCompany.company_id.in_(my_company_ids)).first()
        if not shared:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user: schemas.UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    has_admin = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id, models.UserCompany.role == 'admin').first()
    if not has_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user.dict(exclude={"password"}).items():
        setattr(db_user, key, value)
    
    if user.password:
        db_user.hashed_password = security.get_password_hash(user.password)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    has_admin = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id, models.UserCompany.role == 'admin').first()
    if not has_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}



class RoleUpdate(BaseModel):
    role: str
    company_id: Optional[int] = None


@router.post("/users/{user_id}/role", response_model=schemas.User)
def set_user_role(
    user_id: int,
    payload: RoleUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Permite a un admin de la empresa cambiar el rol (admin/employee) de un usuario de su misma empresa.
    Evita dejar la empresa sin administradores.
    """
    # Determinar la empresa de contexto: prioridad al company_id del payload
    company_context_id: Optional[int] = payload.company_id
    if company_context_id is None:
        first_link = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id).first()
        if not first_link:
            raise HTTPException(status_code=400, detail="User is not member of any company")
        company_context_id = first_link.company_id

    # Exigir admin del usuario autenticado en la empresa de contexto
    admin_link = db.query(models.UserCompany).filter(
        models.UserCompany.user_id == current_user.id,
        models.UserCompany.company_id == company_context_id,
        models.UserCompany.role == 'admin'
    ).first()
    if not admin_link:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    target = db.query(models.User).filter(models.User.id == user_id).first()
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Asegurar que el target pertenece a la misma empresa de contexto
    target_link = db.query(models.UserCompany).filter(
        models.UserCompany.user_id == target.id,
        models.UserCompany.company_id == company_context_id,
    ).first()
    if not target_link:
        raise HTTPException(status_code=403, detail="Action limited to users in your company")

    new_role = (payload.role or "").strip().lower()
    if new_role not in ("admin", "employee"):
        raise HTTPException(status_code=400, detail="Invalid role; must be 'admin' or 'employee'")

    # Si vamos a degradar a un admin, asegurar que no sea el último admin activo
    if target_link.role == 'admin' and new_role != 'admin':
        admins_count = db.query(models.UserCompany).filter(
            models.UserCompany.company_id == company_context_id,
            models.UserCompany.role == 'admin'
        ).count()
        if admins_count <= 1:
            raise HTTPException(status_code=400, detail="Debe permanecer al menos un administrador en la empresa")

    target_link.role = new_role
    db.add(target_link)
    db.commit()
    db.refresh(target)
    return target