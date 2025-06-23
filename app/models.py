from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    correo = Column(String, unique=True)
    tipo = Column(String)  # 'admin' o 'cliente'

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    descripcion = Column(String)
    categoria = Column(String)
    precio = Column(Float)
    stock = Column(Integer)

class Pedido(Base):
    __tablename__ = 'pedidos'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    total = Column(Float)
    confirmado = Column(Boolean, default=False)

    usuario = relationship("Usuario")
    detalles = relationship("PedidoDetalle", cascade="all, delete-orphan")

class PedidoDetalle(Base):
    __tablename__ = 'pedido_detalles'
    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'))
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad = Column(Integer)
    precio_unitario = Column(Float)

    producto = relationship("Producto")
