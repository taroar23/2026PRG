from sqlalchemy import Column, Integer, String, Boolean, Float
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    clave = Column(String(200), nullable=False)
    activo = Column(Boolean, default=True)
    rol = Column(String(20), default="cliente")  # admin / cliente

    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    existencia = Column(Integer, default=0)

    def __repr__(self):
        return f'<Producto {self.nombre}>'
