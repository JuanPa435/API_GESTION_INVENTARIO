from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..db import database

router = APIRouter()


@router.get("/health/db")
def health_db(db: Session = Depends(database.get_db)):
    """Chequeo de salud de la base de datos: ejecuta SELECT 1 y devuelve metadatos básicos."""
    try:
        # SELECT 1 y base actual
        one = db.execute(text("SELECT 1")).scalar()
        try:
            dbname = db.execute(text("SELECT DATABASE()")).scalar()
        except Exception:
            # No-MySQL fallback
            dbname = None
        return {"status": "ok", "one": int(one or 0), "database": dbname}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db_error: {e.__class__.__name__}: {e}")
