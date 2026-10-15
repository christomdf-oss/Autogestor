import models
from sqlalchemy.exc import IntegrityError
from Repository import usuarios as repo
from security import hash_password, verify_password, crear_token

def crear_usuario(db, usuario):
    nuevo = models.Usuario(nombre=usuario.nombre.strip(), email=str(usuario.email).strip().lower(), contraseña=hash_password(usuario.contraseña), rol=usuario.rol, activo=True)
    try:
        return repo.crear_usuario(db, nuevo)
    except IntegrityError:
        db.rollback()
        return None

def iniciar_sesion(db, email, contraseña):
    usuario = repo.obtener_usuario_por_email(db, str(email).strip().lower())
    if not usuario or not usuario.activo or not verify_password(contraseña, usuario.contraseña):
        return None
    return crear_token({"sub": usuario.email, "rol": usuario.rol})
