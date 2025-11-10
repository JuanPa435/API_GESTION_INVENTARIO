from pydantic import BaseModel, EmailStr, conint
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    username: str
    # Sin compañía única ni ranuras; las membresías viven en `user_companies`

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    invite_code: Optional[str] = None

class CompanyCreate(CompanyBase):
    name: str
    invite_code: str

class Company(CompanyBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: conint(ge=0)
    min_quantity: conint(ge=0)
    company_id: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    company_ids: Optional[List[int]] = None