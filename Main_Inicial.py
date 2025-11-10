import uvicorn
import sys
import os

def main():
    # Agregar el directorio backend al path de Python
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    sys.path.append(backend_path)
    
    # Configurar el host y puerto
    host = "0.0.0.0"
    port = 8000
    
    print(f"Iniciando servidor en http://{host}:{port}")
    print(f"Frontend disponible en http://{host}:{port}")
    print(f"API docs disponible en http://{host}:{port}/docs")
    print("Presiona CTRL+C para detener el servidor")
    
    # Iniciar el servidor
    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        reload=True  # Habilitar recarga automática en desarrollo
    )

if __name__ == "__main__":
    main()