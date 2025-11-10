from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)

    # Relación many-to-many con compañías a través de UserCompany
    companies = relationship("UserCompany", back_populates="user")

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True)
    invite_code = Column(String(50), unique=True, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="company")
    # Relación many-to-many con usuarios
    user_links = relationship("UserCompany", back_populates="company")


class UserCompany(Base):
    __tablename__ = 'user_companies'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), primary_key=True)
    role = Column(String(50), default='employee')

    user = relationship('User', back_populates='companies')
    company = relationship('Company', back_populates='user_links')

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True)
    description = Column(String(255))
    quantity = Column(Integer)
    min_quantity = Column(Integer)
    company_id = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company", back_populates="items")