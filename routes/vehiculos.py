
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse, unquote
import io
import os
import logging

import cloudinary
import cloudinary.uploader

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Query
)

from PIL import Image, UnidentifiedImageError

from database import get_db
from services import vehiculos as vehiculos_service
from schemas.vehiculos import Vehiculo, VehiculoResponse
from security import obtener_usuario_actual, verificar_admin
from Repository import vehiculos as vehiculos_repository


router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("static/uploads/vehiculos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_IMAGENES = 10
MAX_BYTES = 5 * 1024 * 1024

FORMATOS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp"
}


def usar_cloudinary():
    return os.getenv(
        "IMAGE_STORAGE", "local"
    ).strip().lower() == "cloudinary"


def configurar_cloudinary():
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not all((cloud_name, api_key, api_secret)):
        raise HTTPException(
            status_code=500,
            detail="Faltan credenciales de Cloudinary"
        )

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )


def obtener_public_id_cloudinary(url):
    """
    Obtiene el identificador de una imagen subida
    por AutoGestor a Cloudinary.
    """
    parsed = urlparse(url)
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")

    if (
        parsed.scheme != "https"
        or parsed.hostname != "res.cloudinary.com"
        or not cloud_name
    ):
        return None

    partes = unquote(parsed.path).split("/")

    if len(partes) < 7:
        return None

    if partes[1] != cloud_name:
        return None

    if partes[2:4] != ["image", "upload"]:
        return None

    resto = partes[4:]

    if (
        resto
        and resto[0].startswith("v")
        and resto[0][1:].isdigit()
    ):
        resto = resto[1:]

    if not resto or resto[0] != "autogestor":
        return None

    if len(resto) < 3 or resto[1] != "vehiculos":
        return None

    public_id = "/".join(resto).rsplit(".", 1)[0]

    return public_id


def borrar_imagen_almacenamiento(url):
    """
    Borra fotografías locales antiguas o imágenes
    almacenadas en Cloudinary.
    """
    prefijo_local = "/static/uploads/vehiculos/"

    if url.startswith(prefijo_local):
        nombre = Path(url).name
        archivo = UPLOAD_DIR / nombre
        archivo.unlink(missing_ok=True)
        return

    public_id = obtener_public_id_cloudinary(url)

    if public_id:
        configurar_cloudinary()

        resultado = cloudinary.uploader.destroy(
            public_id,
            resource_type="image",
            invalidate=True
        )

        if resultado.get("result") not in ("ok", "not found"):
            raise RuntimeError(
                "Cloudinary no pudo eliminar la imagen"
            )


@router.get(
    "/vehiculos",
    response_model=list[VehiculoResponse]
)
def obtener_vehiculos(
    marca: str | None = None,
    modelo: str | None = None,
    precio_min: float | None = Query(default=None, ge=0),
    precio_max: float | None = Query(default=None, ge=0),
    estado: str | None = None,
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=10, ge=1, le=100),
    db=Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    return vehiculos_service.obtener_vehiculos(
        db,
        marca,
        modelo,
        precio_min,
        precio_max,
        pagina,
        limite,
        estado
    )


@router.get(
    "/vehiculos/{id}",
    response_model=VehiculoResponse
)
def obtener_vehiculo(
    id: int,
    db=Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    vehiculo = vehiculos_service.obtener_vehiculo_por_id(
        db,
        id
    )

    if not vehiculo:
        raise HTTPException(
            status_code=404,
            detail="Vehículo no encontrado"
        )

    return vehiculo


@router.post(
    "/vehiculos",
    response_model=VehiculoResponse,
    status_code=201
)
def crear_vehiculo(
    vehiculo: Vehiculo,
    db=Depends(get_db),
    usuario_actual: dict = Depends(verificar_admin)
):
    return vehiculos_service.crear_vehiculo(
        db,
        vehiculo,
        usuario_actual
    )


@router.put(
    "/vehiculos/{id}",
    response_model=VehiculoResponse
)
def actualizar_vehiculo(
    id: int,
    vehiculo_actualizado: Vehiculo,
    db=Depends(get_db),
    usuario_actual: dict = Depends(verificar_admin)
):
    vehiculo = vehiculos_service.actualizar_vehiculo(
        db,
        id,
        vehiculo_actualizado
    )

    if not vehiculo:
        raise HTTPException(
            status_code=404,
            detail="Vehículo no encontrado"
        )

    return vehiculo


@router.delete("/vehiculos/{id}")
def eliminar_vehiculo(
    id: int,
    db=Depends(get_db),
    usuario_actual: dict = Depends(verificar_admin)
):
    rutas = vehiculos_service.eliminar_vehiculo(
        db,
        id
    )

    for ruta in rutas:
        try:
            borrar_imagen_almacenamiento(ruta)
        except Exception:
            logger.exception(
                "No se pudo eliminar una imagen del vehículo %s",
                id
            )

    return {
        "mensaje": "Vehículo eliminado correctamente"
    }


@router.post(
    "/vehiculos/{id}/imagenes",
    status_code=201
)
async def subir_imagen(
    id: int,
    archivo: UploadFile = File(...),
    db=Depends(get_db),
    usuario_actual: dict = Depends(verificar_admin)
):
    vehiculo = vehiculos_service.obtener_vehiculo_por_id(
        db,
        id
    )

    if not vehiculo:
        raise HTTPException(
            status_code=404,
            detail="Vehículo no encontrado"
        )

    cantidad = vehiculos_repository.contar_imagenes(
        db,
        id
    )

    if cantidad >= MAX_IMAGENES:
        raise HTTPException(
            status_code=400,
            detail="Máximo 10 fotografías por vehículo"
        )

    try:
        contenido = await archivo.read(MAX_BYTES + 1)

        if len(contenido) > MAX_BYTES:
            raise HTTPException(
                status_code=413,
                detail="La imagen supera los 5 MB"
            )

        try:
            with Image.open(io.BytesIO(contenido)) as imagen:
                formato = imagen.format
                imagen.verify()

        except (
            UnidentifiedImageError,
            OSError,
            ValueError
        ):
            raise HTTPException(
                status_code=400,
                detail="El archivo no es una imagen válida"
            )

        if formato not in FORMATOS:
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten JPG, PNG o WebP"
            )

        nombre = uuid4().hex

        if usar_cloudinary():
            configurar_cloudinary()

            try:
                resultado = cloudinary.uploader.upload(
                    contenido,
                    folder="autogestor/vehiculos",
                    public_id=nombre,
                    resource_type="image",
                    overwrite=False
                )

                url = resultado["secure_url"]

            except Exception:
                logger.exception(
                    "Error al subir imagen a Cloudinary"
                )
                raise HTTPException(
                    status_code=502,
                    detail="No se pudo subir la imagen a Cloudinary"
                )

        else:
            extension = FORMATOS[formato]
            nombre_archivo = f"{nombre}{extension}"
            destino = UPLOAD_DIR / nombre_archivo

            try:
                destino.write_bytes(contenido)

            except OSError:
                raise HTTPException(
                    status_code=500,
                    detail="No se pudo guardar la imagen"
                )

            url = (
                f"/static/uploads/vehiculos/"
                f"{nombre_archivo}"
            )

        try:
            imagen_db = vehiculos_repository.agregar_imagen(
                db,
                id,
                url,
                principal=(cantidad == 0)
            )

        except Exception:
            db.rollback()

            try:
                borrar_imagen_almacenamiento(url)
            except Exception:
                logger.exception(
                    "No se pudo limpiar la imagen tras error de BD"
                )

            raise

        return {
            "id": imagen_db.id,
            "url": imagen_db.url,
            "principal": imagen_db.principal
        }

    finally:
        await archivo.close()


@router.delete(
    "/vehiculos/{id}/imagenes/{imagen_id}"
)
def eliminar_imagen(
    id: int,
    imagen_id: int,
    db=Depends(get_db),
    usuario_actual: dict = Depends(verificar_admin)
):
    imagen = vehiculos_repository.obtener_imagen_por_id(
        db,
        imagen_id
    )

    if not imagen or imagen.vehiculo_id != id:
        raise HTTPException(
            status_code=404,
            detail="Imagen no encontrada"
        )

    era_principal = imagen.principal
    url = imagen.url

    vehiculos_repository.eliminar_imagen(
        db,
        imagen
    )

    if era_principal:
        vehiculo = vehiculos_repository.obtener_vehiculo_por_id(
            db,
            id
        )

        if vehiculo and vehiculo.imagenes:
            vehiculos_repository.establecer_imagen_principal(
                db,
                id,
                vehiculo.imagenes[0].id
            )

    try:
        borrar_imagen_almacenamiento(url)

    except Exception:
        logger.exception(
            "No se pudo eliminar la imagen del almacenamiento"
        )

    return {
        "mensaje": "Imagen eliminada correctamente"
    }


@router.put(
    "/vehiculos/{id}/imagenes/{imagen_id}/principal"
)
def cambiar_imagen_principal(
    id: int,
    imagen_id: int,
    db=Depends(get_db),
    usuario_actual: dict = Depends(verificar_admin)
):
    imagen = vehiculos_repository.obtener_imagen_por_id(
        db,
        imagen_id
    )

    if not imagen or imagen.vehiculo_id != id:
        raise HTTPException(
            status_code=404,
            detail="Imagen no encontrada"
        )

    vehiculos_repository.establecer_imagen_principal(
        db,
        id,
        imagen_id
    )

    return {
        "mensaje": "Portada actualizada correctamente"
    }
