
import models

from fastapi import HTTPException

from Repository import vehiculos as vehiculos_repository
from Repository import usuarios as usuarios_repository


def crear_vehiculo(db, vehiculo, usuario_actual):
    usuario = usuarios_repository.obtener_usuario_por_email(
        db,
        usuario_actual["sub"]
    )

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    nuevo_vehiculo = models.Vehiculo(
        **vehiculo.model_dump(),
        usuario_id=usuario.id
    )

    return vehiculos_repository.crear_vehiculo(
        db,
        nuevo_vehiculo
    )


def obtener_vehiculos(
    db,
    marca=None,
    modelo=None,
    precio_min=None,
    precio_max=None,
    pagina=1,
    limite=10,
    estado=None
):
    return vehiculos_repository.obtener_vehiculos(
        db,
        marca,
        modelo,
        precio_min,
        precio_max,
        pagina,
        limite,
        estado
    )


def obtener_vehiculo_por_id(db, id):
    return vehiculos_repository.obtener_vehiculo_por_id(
        db,
        id
    )


def actualizar_vehiculo(db, id, vehiculo_actualizado):
    return vehiculos_repository.actualizar_vehiculo(
        db,
        id,
        vehiculo_actualizado
    )


def eliminar_vehiculo(db, id):
    vehiculo = vehiculos_repository.obtener_vehiculo_por_id(
        db,
        id
    )

    if not vehiculo:
        raise HTTPException(
            status_code=404,
            detail="Vehículo no encontrado"
        )

    rutas_imagenes = [
        imagen.url for imagen in vehiculo.imagenes
    ]

    vehiculos_repository.eliminar_vehiculo(
        db,
        vehiculo
    )

    return rutas_imagenes
