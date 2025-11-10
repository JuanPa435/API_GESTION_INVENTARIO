from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .routers import auth, users, companies, inventory, health
from .db.database import engine, Base

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Gestión de Inventario",
    description="API para gestionar inventario con autenticación y múltiples empresas",
    version="1.0.0",
    docs_url="/docs",  # Especificar la ruta de la documentación
    redoc_url="/redoc",  # Especificar la ruta de la documentación alternativa
    openapi_url="/api/openapi.json"  # Especificar la ruta del esquema OpenAPI
)

# Configurar CORS - Permitir todos los orígenes en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(companies.router, prefix="/api", tags=["companies"])
app.include_router(inventory.router, prefix="/api", tags=["inventory"])
app.include_router(health.router, prefix="/api", tags=["health"]) 

# Configurar archivos estáticos para el frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend')
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")