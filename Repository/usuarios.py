import models


def crear_usuario(db, nuevo_usuario):
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


def obtener_usuario_por_email(db, email):
    return (
        db.query(models.Usuario)
        .filter(models.Usuario.email == email)
        .first()
    )


def obtener_usuario_por_id(db, id):
    return (
        db.query(models.Usuario)
        .filter(models.Usuario.id == id)
        .first()
    )


def listar_usuarios(db):
    return (
        db.query(models.Usuario)
        .order_by(models.Usuario.id)
        .all()
    )


def actualizar_usuario(db, usuario, cambios):
    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)

    return usuario