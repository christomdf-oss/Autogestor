from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Literal

from database import get_db
from security import obtener_usuario_actual, verificar_admin
from schemas.usuarios import UsuarioCreate, UsuarioResponse
from services import usuarios as usuarios_service
from Repository import usuarios as usuarios_repository

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    contraseña: str


class UsuarioUpdate(BaseModel):
    rol: Literal["admin", "usuario"] | None = None
    activo: bool | None = None


@router.post("/login")
def iniciar_sesion(
    datos: LoginRequest,
    db: Session = Depends(get_db)
):
    token = usuarios_service.iniciar_sesion(
        db,
        datos.email,
        datos.contraseña
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/usuarios/me")
def obtener_perfil(
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    return usuario_actual


@router.get("/usuarios")
def listar_usuarios(
    db: Session = Depends(get_db),
    admin: dict = Depends(verificar_admin)
):
    return usuarios_repository.listar_usuarios(db)


@router.post(
    "/usuarios",
    response_model=UsuarioResponse,
    status_code=201
)
def crear_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(verificar_admin)
):
    nuevo_usuario = usuarios_service.crear_usuario(db, usuario)

    if not nuevo_usuario:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    return nuevo_usuario


@router.patch("/usuarios/{usuario_id}")
def actualizar_usuario(
    usuario_id: int,
    cambios: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(verificar_admin)
):
    usuario = usuarios_repository.obtener_usuario_por_id(
        db,
        usuario_id
    )

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    datos = cambios.model_dump(exclude_unset=True)

    if not datos:
        raise HTTPException(
            status_code=400,
            detail="No se enviaron cambios"
        )

    if any(valor is None for valor in datos.values()):
        raise HTTPException(
            status_code=422,
            detail="Los campos no pueden ser nulos"
        )

    # No permitir que el administrador modifique
    # su propio rol o desactive su cuenta.
    if usuario.email == admin.get("sub"):
        if datos.get("activo") is False:
            raise HTTPException(
                status_code=403,
                detail="No puedes desactivar tu propia cuenta"
            )

        if "rol" in datos and datos["rol"] != "admin":
            raise HTTPException(
                status_code=403,
                detail="No puedes quitarte el rol de administrador"
            )

    return usuarios_repository.actualizar_usuario(
        db,
        usuario,
        datos
    )