from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    año = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    kilometraje = Column(Integer, nullable=False, default=0)
    color = Column(String(50), nullable=False, default="No especificado")
    descripcion = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="disponible")
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="vehiculos")
    imagenes = relationship("VehiculoImagen", back_populates="vehiculo", cascade="all, delete-orphan", order_by="VehiculoImagen.id")

class VehiculoImagen(Base):
    __tablename__ = "vehiculo_imagenes"
    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    principal = Column(Boolean, nullable=False, default=False)
    vehiculo = relationship("Vehiculo", back_populates="imagenes")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    contraseña = Column(String, nullable=False)
    rol = Column(String(20), nullable=False, default="usuario")
    activo = Column(Boolean, nullable=False, default=True, server_default="true")
    vehiculos = relationship("Vehiculo", back_populates="usuario")
