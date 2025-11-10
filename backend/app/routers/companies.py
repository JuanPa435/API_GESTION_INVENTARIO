from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..db import models, schemas, database
from ..auth.dependencies import get_current_active_user
from ..auth import security
from pydantic import BaseModel

router = APIRouter()

@router.post("/companies/", response_model=schemas.Company)
def create_company(
    company: schemas.CompanyCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user),
    response: Response = None,
):
    # Permitir creación a cualquier usuario autenticado y auto-asignarlo como admin de la nueva empresa

    # Normalizar y validar código
    code = (company.invite_code or "").strip().upper()
    if not code or len(code) < 4 or len(code) > 50:
        raise HTTPException(status_code=400, detail="El código debe tener entre 4 y 50 caracteres")
    if not all(c.isalnum() or c == '-' for c in code):
        raise HTTPException(status_code=400, detail="El código solo puede contener letras, números o guiones (-)")

    db_company = models.Company(name=company.name.strip(), description=company.description, invite_code=code)
    db.add(db_company)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Nombre o código ya está en uso")
    db.refresh(db_company)

    # Auto-asociar al creador como admin
    try:
        link = models.UserCompany(user_id=current_user.id, company_id=db_company.id, role='admin')
        db.add(link)
        db.commit()
    except IntegrityError:
        db.rollback()
        # Si ya estaba asociado, continuar
        pass

    # Refrescar token para incluir la nueva empresa
    try:
        links = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id).all()
        company_ids = [l.company_id for l in links]
        access_token = security.create_access_token(data={
            "sub": current_user.username,
            "company_ids": company_ids,
            "company_id": db_company.id,
        })
        if isinstance(response, Response):
            response.headers["X-New-Token"] = access_token
    except Exception:
        pass

    return db_company


@router.post("/companies/self-create", response_model=schemas.Company)
def self_create_company(
    company: schemas.CompanyCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user),
    response: Response = None,
):
    """Permite a un usuario autenticado crear una compañía y asignarse como admin.
    - Si el usuario ya pertenece a una compañía, devuelve 400.
    """
    # Verificar límite de compañías por usuario (máx 5)
    memberships = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id).count()
    if memberships >= 5:
        raise HTTPException(status_code=400, detail="User already belongs to the maximum allowed companies (5)")

    # Normalizar y validar código
    code = (company.invite_code or "").strip().upper()
    if not code or len(code) < 4 or len(code) > 50:
        raise HTTPException(status_code=400, detail="El código debe tener entre 4 y 50 caracteres")
    if not all(c.isalnum() or c == '-' for c in code):
        raise HTTPException(status_code=400, detail="El código solo puede contener letras, números o guiones (-)")

    # Crear compañía
    db_company = models.Company(name=company.name.strip(), description=company.description, invite_code=code)
    db.add(db_company)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Nombre o código ya está en uso")
    db.refresh(db_company)

    # Crear enlace en la tabla de asociación y asignar rol admin
    link = models.UserCompany(user_id=current_user.id, company_id=db_company.id, role='admin')
    db.add(link)
    db.commit()

    # Refrescar token con nuevas compañías del usuario y establecerlo en cabecera
    try:
        links = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id).all()
        company_ids = [l.company_id for l in links]
        # incluir también company_id actual para flujos que lo usan
        access_token = security.create_access_token(data={
            "sub": current_user.username,
            "company_ids": company_ids,
            "company_id": db_company.id,
        })
        if isinstance(response, Response):
            response.headers["X-New-Token"] = access_token
    except Exception:
        # No bloquear la creación si falla la actualización del token
        pass

    return db_company


class JoinCompanyPayload(BaseModel):
    company_id: Optional[int] = None
    code: Optional[str] = None


class MyRoleResponse(BaseModel):
    role: str


@router.post("/companies/join", response_model=schemas.Company)
def join_company(
    payload: JoinCompanyPayload,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user),
    response: Response = None,
):
    """Unirse a una empresa por ID (o código numérico temporal).
    Nota: en el futuro puede cambiarse a códigos de invitación alfanuméricos.
    """
    # Verificar límite de compañías por usuario (máx 5)
    memberships = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id).count()
    if memberships >= 5:
        raise HTTPException(status_code=400, detail="User already belongs to the maximum allowed companies (5)")

    company_id: Optional[int] = payload.company_id
    target_company: Optional[models.Company] = None
    if company_id is None and payload.code:
        code = payload.code.strip().upper()
        # Si es numérico puro, interpretarlo como ID; si no, buscar por invite_code
        if code.isdigit():
            company_id = int(code)
        else:
            target_company = db.query(models.Company).filter(models.Company.invite_code == code).first()

    if target_company is None and company_id is None:
        raise HTTPException(status_code=400, detail="company_id or code is required")

    company = target_company or db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Crear enlace en la tabla de asociación como employee
    try:
        link = models.UserCompany(user_id=current_user.id, company_id=company.id, role='employee')
        db.add(link)
        db.commit()
    except IntegrityError:
        db.rollback()
        # Ya estaba asociado
        pass

    # Refrescar token con lista actualizada e incluir company_id
    try:
        links = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id).all()
        company_ids = [l.company_id for l in links]
        access_token = security.create_access_token(data={
            "sub": current_user.username,
            "company_ids": company_ids,
            "company_id": company.id,
        })
        if isinstance(response, Response):
            response.headers["X-New-Token"] = access_token
    except Exception:
        pass
    return company

@router.get("/companies/", response_model=List[schemas.Company])
def read_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Requerir ser admin en alguna empresa para listar todas las compañías
    has_admin = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id, models.UserCompany.role == 'admin').first()
    if not has_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    companies = db.query(models.Company).offset(skip).limit(limit).all()
    return companies


@router.get("/companies/my", response_model=List[schemas.Company])
def read_my_companies(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Devuelve las compañías a las que pertenece el usuario autenticado.
    No requiere rol de admin; lista únicamente las del propio usuario.
    """
    companies = (
        db.query(models.Company)
        .join(models.UserCompany, models.Company.id == models.UserCompany.company_id)
        .filter(models.UserCompany.user_id == current_user.id)
        .distinct()
        .all()
    )
    return companies

@router.get("/companies/{company_id}", response_model=schemas.Company)
def read_company(
    company_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Permitir si el usuario pertenece a la compañía (cualquier rol)
    link = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id, models.UserCompany.company_id == company_id).first()
    if link is None:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/companies/{company_id}/my-role", response_model=MyRoleResponse)
def get_my_role(
    company_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    link = db.query(models.UserCompany).filter(
        models.UserCompany.user_id == current_user.id,
        models.UserCompany.company_id == company_id
    ).first()
    if link is None:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return MyRoleResponse(role=link.role or 'employee')

@router.put("/companies/{company_id}", response_model=schemas.Company)
def update_company(
    company_id: int,
    company: schemas.CompanyCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Sólo admin de la compañía puede actualizar
    link = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id, models.UserCompany.company_id == company_id).first()
    if link is None or link.role != 'admin':
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    for key, value in company.dict().items():
        setattr(db_company, key, value)
    
    db.commit()
    db.refresh(db_company)
    return db_company

@router.delete("/companies/{company_id}")
def delete_company(
    company_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Sólo admin de la compañía puede eliminar
    link = db.query(models.UserCompany).filter(models.UserCompany.user_id == current_user.id, models.UserCompany.company_id == company_id).first()
    if link is None or link.role != 'admin':
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Eliminar enlaces de asociación primero para evitar conflictos de PK/FK
    db.query(models.UserCompany).filter(models.UserCompany.company_id == company_id).delete(synchronize_session=False)
    
    db.delete(company)
    db.commit()
    return {"message": "Company deleted successfully"}