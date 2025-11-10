# InvenTech - Sistema de Gestión de Inventario

Sistema web completo de gestión de inventario con autenticación JWT, control de permisos basado en roles y gestión de productos.

## 🚀 Características

### ✅ Implementado
- **Autenticación JWT** - Login/Registro seguro
- **Multi-empresa** - Soporte para múltiples empresas
- **Control de Permisos** - Roles Admin/Employee
- **CRUD de Productos** - Crear, leer, actualizar, eliminar
- **Búsqueda y Filtrado** - Buscar productos por nombre
- **Base de datos MySQL** - Railway cloud database
- **API REST** - FastAPI con endpoints documentados
- **Frontend Moderno** - HTML5, CSS3, JavaScript vanilla

### 🔐 Control de Permisos

**Administrador (admin):**
- ✅ Crear productos
- ✅ Editar productos
- ✅ Eliminar productos
- ✅ Ver todos los productos

**Empleado (employee):**
- ✅ Ver productos (solo lectura)
- ❌ No puede crear
- ❌ No puede editar
- ❌ No puede eliminar

## 📁 Estructura del Proyecto

```
API_GESTION_INVENTARIO/
├── backend/
│   ├── app/
│   │   ├── auth/               # Autenticación JWT
│   │   │   ├── dependencies.py
│   │   │   └── security.py
│   │   ├── db/                 # Modelos y schemas
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── routers/            # Endpoints API
│   │   │   ├── auth.py
│   │   │   ├── companies.py
│   │   │   ├── inventory.py    # Productos CRUD
│   │   │   ├── users.py
│   │   │   └── health.py
│   │   └── main.py             # Configuración FastAPI
│   └── requirements.txt
├── frontend/
│   ├── pages/
│   │   ├── productos.html      # Gestión de productos
│   │   ├── company-home.html   # Home empresa
│   │   ├── menu.html
│   │   └── ...
│   ├── css/
│   │   ├── products.css
│   │   ├── base.css
│   │   └── ...
│   ├── js/
│   │   ├── products.js
│   │   ├── auth.js
│   │   └── ...
│   └── index.html
├── .env                        # Variables de entorno
└── README.md
```

## 🛠️ Stack Tecnológico

**Backend:**
- Python 3.12
- FastAPI
- SQLAlchemy ORM
- PyMySQL (MySQL driver)
- JWT (autenticación)
- Uvicorn (servidor ASGI)

**Frontend:**
- HTML5
- CSS3
- JavaScript vanilla
- Fetch API

**Database:**
- MySQL (Railway)

## ⚙️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/JuanPa435/API_GESTION_INVENTARIO.git
cd API_GESTION_INVENTARIO
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales de Railway
```

### 5. Ejecutar servidor
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Acceder a la aplicación
- Frontend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 🔑 Credenciales de Test

**Usuario Admin:**
- Email: `jp@gmail.com`
- Contraseña: `jp`
- Empresa: `jp` (ID: 3)
- Rol: `admin`

## 📝 Endpoints API

### Autenticación
- `POST /token` - Obtener JWT token
- `POST /api/register` - Registrar nuevo usuario

### Empresas
- `GET /api/companies/my` - Mis empresas
- `GET /api/companies/{id}` - Detalles empresa
- `GET /api/companies/{id}/my-role` - Mi rol en empresa

### Productos (Inventario)
- `GET /api/company/{id}/items/` - Listar productos
- `POST /api/items/` - Crear producto (admin)
- `PUT /api/items/{id}` - Editar producto (admin)
- `DELETE /api/items/{id}` - Eliminar producto (admin)

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ JWT tokens con expiración
- ✅ CORS habilitado para desarrollo
- ✅ Validación de permisos en cada endpoint
- ✅ Validación de datos con Pydantic

## 📊 Base de Datos

**Tablas:**
- `users` - Usuarios del sistema
- `companies` - Empresas
- `user_companies` - Relación usuario-empresa con rol
- `items` - Productos del inventario

## 🚀 Próximas Características

- [ ] Dashboard de analytics
- [ ] Reportes PDF
- [ ] Categorías de productos
- [ ] Proveedores
- [ ] Movimientos de inventario
- [ ] Notificaciones de stock bajo
- [ ] Exportar/Importar CSV

## 📄 Licencia

MIT License

## 👥 Autor

Juan Pablo - [@JuanPa435](https://github.com/JuanPa435)

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para reportar bugs o solicitar features, abre un issue en el repositorio.
