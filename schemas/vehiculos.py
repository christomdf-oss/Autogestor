
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class Vehiculo(BaseModel):
    marca: str = Field(min_length=1, max_length=50)
    modelo: str = Field(min_length=1, max_length=50)
    año: int = Field(gt=1900, le=2100)
    precio: float = Field(gt=0)

    kilometraje: int = Field(default=0, ge=0)
    color: str = Field(default="No especificado", min_length=1, max_length=50)
    descripcion: str | None = Field(default=None, max_length=2000)

    estado: Literal[
        "disponible",
        "apartado",
        "vendido"
    ] = "disponible"


class VehiculoImagenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    principal: bool


class VehiculoResponse(Vehiculo):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    imagenes: list[VehiculoImagenResponse] = []
