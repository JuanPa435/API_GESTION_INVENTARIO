from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Permite configurar por variable de entorno; por defecto, usa la BD MySQL proporcionada
# Nota: para SQLAlchemy con MySQL usaremos el driver PyMySQL
DEFAULT_MYSQL_URL = (
    "mysql+pymysql://root:AZPSzWrueTQRxGWZjUnBGvSoywOqScAm@hopper.proxy.rlwy.net:57628/railway"
)

# Admitir cadena sin el prefijo de driver (mysql://) y normalizar a mysql+pymysql://
_db_url = os.getenv("DATABASE_URL", DEFAULT_MYSQL_URL)
if _db_url.startswith("mysql://"):
    _db_url = "mysql+pymysql://" + _db_url[len("mysql://"):]
SQLALCHEMY_DATABASE_URL = _db_url

# Configuración del engine según el dialecto
engine_kwargs = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # Solo SQLite requiere este connect_arg
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # MySQL/Postgres: mantener la conexión viva y validar
    engine_kwargs["pool_pre_ping"] = True
    # Reciclar conexiones inactivas para evitar 'MySQL server has gone away'
    engine_kwargs["pool_recycle"] = 1800  # 30 minutos

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()