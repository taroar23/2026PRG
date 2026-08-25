from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    clave = Column(String(200), nullable=False)
    activo = Column(Boolean, default=True)
    rol = Column(String(20), default="cliente")
    foto_perfil = Column(Text, nullable=True)  # Base64 o URL de foto de perfil

    compras = relationship("Compra", back_populates="usuario")

    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    existencia = Column(Integer, default=0)

    detalles = relationship("DetalleCompra", back_populates="producto")

    def __repr__(self):
        return f'<Producto {self.nombre}>'

class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    total = Column(Float, nullable=False)
    estado = Column(String(30), default="completada")

    usuario = relationship("Usuario", back_populates="compras")
    detalles = relationship("DetalleCompra", back_populates="compra")

    def __repr__(self):
        return f'<Compra {self.id} - Usuario {self.usuario_id}>'

class DetalleCompra(Base):
    __tablename__ = "detalle_compras"

    id = Column(Integer, primary_key=True, index=True)
    compra_id = Column(Integer, ForeignKey("compras.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    nombre_producto = Column(String(100), nullable=False)
    precio_unitario = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)

    compra = relationship("Compra", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles")

    def __repr__(self):
        return f'<DetalleCompra compra={self.compra_id} prod={self.nombre_producto}>'
