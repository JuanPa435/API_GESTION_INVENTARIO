# API de Gestión de Inventario

Backend desarrollado con FastAPI y SQLite. El backend proporciona una API REST segura con JWT para la gestión de empresas e inventario.

## Características

- Login y registro de usuarios
- Autenticación JWT para proteger rutas
- Roles (admin/employee) 
- Empresas con empleados e inventario
- API REST para CRUD de items
- Documentación automática con Swagger UI

## Instalación

1. Crear entorno virtual:
```bash
python3 -m venv backend/venv
```

2. Activar entorno:
```bash
source backend/venv/bin/activate  # Linux/Mac
backend\venv\Scripts\activate  # Windows
```

3. Instalar dependencias:
```bash 
pip install -r backend/requirements.txt
```

4. Correr la API:
```bash
uvicorn backend.main:app --reload
```

5. Abrir http://localhost:8000/docs para ver la documentación de la API

## Frontend

Frontend simple en `frontend/`. Solo abrir `frontend/index.html` en el navegador apuntando a la API backend en localhost:8000.

## Estructura

```
.
├── backend/             # Backend FastAPI
│   ├── venv/           # Entorno virtual Python 
│   ├── app/            # Código fuente
│   │   ├── models.py     # Modelos SQLAlchemy
│   │   ├── schemas.py    # Schemas Pydantic
│   │   ├── security.py   # JWT y auth
│   │   └── routers/      # Endpoints API
│   ├── main.py         # Entrada FastAPI
│   └── requirements.txt # Dependencias
└── frontend/           # Frontend estático