import os
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from database import get_db
import models

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("No se encontró SECRET_KEY en .env")
ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()
security = HTTPBearer(auto_error=False)

def hash_password(password):
    return password_hash.hash(password)

def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)

def crear_token(data, minutos_expiracion=30):
    datos = data.copy()
    datos["exp"] = datetime.now(timezone.utc) + timedelta(minutes=minutos_expiracion)
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario_actual(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Debes iniciar sesión", headers={"WWW-Authenticate": "Bearer"})
    try:
        datos = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = datos.get("sub")
        if not isinstance(email, str) or not email:
            raise InvalidTokenError("Token sin usuario")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado", headers={"WWW-Authenticate": "Bearer"})
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if usuario is None or not usuario.activo:
        raise HTTPException(status_code=401, detail="Cuenta inexistente o desactivada")
    # Mantiene la interfaz del diccionario que ya consumen routes/vehiculos.py.
    # El rol siempre proviene de PostgreSQL, no del JWT antiguo.
    return {"sub": usuario.email, "rol": usuario.rol, "id": usuario.id, "nombre": usuario.nombre}

def verificar_admin(usuario_actual: dict = Depends(obtener_usuario_actual)):
    if usuario_actual["rol"] != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para realizar esta acción")
    return usuario_actual
