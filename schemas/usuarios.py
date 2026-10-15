from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Literal

class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)
    email: EmailStr
    contraseña: str = Field(min_length=8, max_length=100)
    rol: Literal["admin", "usuario"] = "usuario"

class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: bool

class UsuarioActualizar(BaseModel):
    rol: Literal["admin", "usuario"] | None = None
    activo: bool | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    contraseña: str
