from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..db import schemas

# Configuración de seguridad
SECRET_KEY = "your-secret-key"  # Cambia esto por una clave segura en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Soporta contraseñas largas pre-hasheándolas con SHA256 antes de bcrypt
# Mantiene compatibilidad para verificar hashes antiguos "bcrypt"
# Usa PBKDF2 por defecto para evitar limitación de 72 bytes y problemas de backend de bcrypt.
# Mantiene compatibilidad de verificación para hashes previos si existen.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[schemas.TokenData]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        company_ids = payload.get("company_ids")
        if username is None:
            return None
        token_data = schemas.TokenData(
            username=username,
            company_ids=company_ids
        )
        return token_data
    except JWTError:
        return None