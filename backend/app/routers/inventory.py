from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import models, schemas, database
from ..auth.dependencies import get_current_active_user

router = APIRouter()

@router.post("/items/", response_model=schemas.Item)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Verificar que el usuario pertenece a la empresa
    user_company = db.query(models.UserCompany).filter(
        models.UserCompany.user_id == current_user.id,
        models.UserCompany.company_id == item.company_id
    ).first()
    
    if not user_company:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/items/", response_model=List[schemas.Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Obtener las empresas a las que pertenece el usuario
    user_companies = db.query(models.UserCompany).filter(
        models.UserCompany.user_id == current_user.id
    ).all()
    
    company_ids = [uc.company_id for uc in user_companies]
    
    if not company_ids:
        return []
    
    items = db.query(models.Item).filter(
        models.Item.company_id.in_(company_ids)
    ).offset(skip).limit(limit).all()
    
    return items

@router.get("/items/{item_id}", response_model=schemas.Item)
def read_item(
    item_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verificar que el usuario pertenece a la empresa del producto
    user_company = db.query(models.UserCompany).filter(
        models.UserCompany.user_id == current_user.id,
        models.UserCompany.company_id == item.company_id
    ).first()
    
    if not user_company:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return item

@router.put("/items/{item_id}", response_model=schemas.Item)
def update_item(
    item_id: int,
    item: schemas.ItemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verificar que el usuario pertenece a la empresa del producto
    user_company = db.query(models.UserCompany).filter(
        models.UserCompany.user_id == current_user.id,
        models.UserCompany.company_id == db_item.company_id
    ).first()
    
    if not user_company:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Verificar que el usuario es administrador
    if user_company.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden editar productos")
    
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verificar que el usuario pertenece a la empresa del producto
    user_company = db.query(models.UserCompany).filter(
        models.UserCompany.user_id == current_user.id,
        models.UserCompany.company_id == item.company_id
    ).first()
    
    if not user_company:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Verificar que el usuario es administrador
    if user_company.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar productos")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}

@router.get("/company/{company_id}/items/", response_model=List[schemas.Item])
def read_company_items(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Verificar que el usuario pertenece a la empresa
    user_company = db.query(models.UserCompany).filter(
        models.UserCompany.user_id == current_user.id,
        models.UserCompany.company_id == company_id
    ).first()
    
    if not user_company:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    items = db.query(models.Item).filter(
        models.Item.company_id == company_id
    ).offset(skip).limit(limit).all()
    return items