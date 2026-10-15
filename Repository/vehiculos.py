
import models


def obtener_vehiculo_por_id(db, id):
    return db.query(models.Vehiculo).filter(
        models.Vehiculo.id == id
    ).first()


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
    consulta = db.query(models.Vehiculo)

    if marca:
        consulta = consulta.filter(
            models.Vehiculo.marca.ilike(f"%{marca}%")
        )

    if modelo:
        consulta = consulta.filter(
            models.Vehiculo.modelo.ilike(f"%{modelo}%")
        )

    if precio_min is not None:
        consulta = consulta.filter(
            models.Vehiculo.precio >= precio_min
        )

    if precio_max is not None:
        consulta = consulta.filter(
            models.Vehiculo.precio <= precio_max
        )

    if estado:
        consulta = consulta.filter(
            models.Vehiculo.estado == estado
        )

    offset = (pagina - 1) * limite

    return (
        consulta
        .order_by(models.Vehiculo.id.desc())
        .offset(offset)
        .limit(limite)
        .all()
    )


def crear_vehiculo(db, nuevo_vehiculo):
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)

    return nuevo_vehiculo


def actualizar_vehiculo(db, id, vehiculo_actualizado):
    vehiculo = obtener_vehiculo_por_id(db, id)

    if not vehiculo:
        return None

    datos = vehiculo_actualizado.model_dump()

    for campo, valor in datos.items():
        setattr(vehiculo, campo, valor)

    db.commit()
    db.refresh(vehiculo)

    return vehiculo


def eliminar_vehiculo(db, vehiculo):
    db.delete(vehiculo)
    db.commit()


def agregar_imagen(db, vehiculo_id, url, principal=False):
    imagen = models.VehiculoImagen(
        vehiculo_id=vehiculo_id,
        url=url,
        principal=principal
    )

    db.add(imagen)
    db.commit()
    db.refresh(imagen)

    return imagen


def obtener_imagen_por_id(db, imagen_id):
    return db.query(models.VehiculoImagen).filter(
        models.VehiculoImagen.id == imagen_id
    ).first()


def contar_imagenes(db, vehiculo_id):
    return db.query(models.VehiculoImagen).filter(
        models.VehiculoImagen.vehiculo_id == vehiculo_id
    ).count()


def eliminar_imagen(db, imagen):
    db.delete(imagen)
    db.commit()


def establecer_imagen_principal(db, vehiculo_id, imagen_id):
    imagenes = db.query(models.VehiculoImagen).filter(
        models.VehiculoImagen.vehiculo_id == vehiculo_id
    ).all()

    for imagen in imagenes:
        imagen.principal = imagen.id == imagen_id

    db.commit()
