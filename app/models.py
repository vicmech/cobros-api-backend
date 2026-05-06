from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from app.special_types import pay_method, estado_cuota, resultado_visita, intervalo_cobro, caja_status

class Distritos(Base):
    __tablename__ = "distritos"

    id_distrito = Column(Integer, primary_key=True, index=True)
    nombre_distrito = Column(String, nullable=False)
    id_provincia = Column(Integer, ForeignKey("provincias.id_provincia"))
    provincia = relationship("Provincias")

class Clientes(Base):
    __tablename__ = "clientes"

    id_cliente = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    telefono = Column(String)
    id_distrito = Column(Integer, ForeignKey("distritos.id_distrito"))
    calle = Column(String)
    casa = Column(String)
    distrito = relationship("Distritos")
    creditos = relationship("Creditos", back_populates="cliente")

class Creditos(Base):
    __tablename__ = "creditos"

    id_credito = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    id_cliente = Column(String, ForeignKey("clientes.id_cliente"))
    id_trabajador = Column(String, ForeignKey("trabajadores.id_trabajador"))
    tiempo_credito = Column(String, nullable=False)
    fecha_inicial = Column(Date, nullable=False)
    fecha_final = Column(Date, nullable=False)
    monto_total = Column(Float, nullable=False)
    intervalo_cobro = Column(Enum(intervalo_cobro), nullable=False)
    origen_monto = Column(Enum(pay_method), nullable=True)
    cliente = relationship("Clientes", back_populates="creditos")
    detalles = relationship("Detalles", back_populates="credito")
    trabajador = relationship("Trabajadores", back_populates="creditos")
    cuotas = relationship('Cuotas', back_populates='credito')

class Detalles(Base):
    __tablename__ = "detalles"

    id_detalle = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    id_credito = Column(String, ForeignKey("creditos.id_credito"))
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    cantidad = Column(Integer, nullable=False)
    credito = relationship("Creditos", back_populates="detalles")
    producto = relationship("Productos")

class Productos(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    detalles = relationship("Detalles", back_populates="producto")

class Trabajadores(Base):
    __tablename__ = "trabajadores"

    id_trabajador = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    telefono = Column(String)
    id_user = Column(String, nullable=False)
    creditos = relationship("Creditos", back_populates="trabajador")
    cajas_diarias = relationship("Cajas_Diarias", back_populates="trabajador")
    pagos = relationship("Pagos", back_populates="trabajador")
    visitas = relationship('Visitas', back_populates='trabajador')

class Users(Base):
    __tablename__ = "users"

    id_user = Column(String, primary_key=True, index=True, default=lambda : str(uuid.uuid4()))
    username = Column(String, nullable=False)
    pwd = Column(String, nullable=False)
    id_role = Column(Integer, ForeignKey("roles.id_rol"))
    email = Column(String, nullable=False)
    roles = relationship("Roles", back_populates='users')

class Roles(Base):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    users = relationship("Users", back_populates="roles")
    
class Pagos(Base):
    __tablename__ = "pagos"

    id_pago = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    id_trabajador = Column(String, ForeignKey("trabajadores.id_trabajador"))
    id_cuota = Column(String, ForeignKey('cuotas.id_cuota'))
    monto = Column(Float, nullable=False)
    fecha_pago = Column(Date, nullable=False)
    metodo_pago = Column(Enum(pay_method), nullable=False)
    trabajador = relationship("Trabajadores", back_populates="pagos")
    cuota = relationship("Cuotas", back_populates="pagos")
    @property
    def credito(self):
        return self.cuota.credito if self.cuota else None
class Provincias(Base):
    __tablename__ = "provincias"

    id_provincia = Column(Integer, primary_key=True, index=True)
    nombre_provincia = Column(String, nullable=False)

class Cajas_Diarias(Base):
    __tablename__ = "cajas_diarias"

    id_caja = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    id_trabajador = Column(String, ForeignKey("trabajadores.id_trabajador"))
    fecha = Column(Date, nullable=False)
    monto_base = Column(Float, nullable=False)
    renovaciones = Column(Float, nullable = False)
    status = Column(Enum(caja_status), nullable=False, default= caja_status.ASIGNADA)
    gastos = relationship("Gastos", back_populates="caja")
    trabajador = relationship("Trabajadores", back_populates="cajas_diarias")

class Gastos(Base):
    __tablename__ = "gastos"

    id_gasto = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    id_caja = Column(String, ForeignKey("cajas_diarias.id_caja"))
    importe = Column(Float, nullable=False)
    descripcion = Column(String, nullable=False)
    caja = relationship("Cajas_Diarias", back_populates="gastos")

class Cuotas(Base):
    __tablename__ = "cuotas"

    id_cuota = Column(String, primary_key=True, index=True, default= lambda: str(uuid.uuid4()))
    id_credito = Column(String, ForeignKey('creditos.id_credito'))
    nro_cuota = Column(Integer, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    monto = Column(Float, nullable=False)
    estado = Column(Enum(estado_cuota), nullable=False, default='PENDIENTE')
    credito = relationship("Creditos", back_populates='cuotas')
    pagos = relationship("Pagos", back_populates="cuota")
    visitas = relationship("Visitas", back_populates="cuota")

class Visitas(Base):
    __tablename__ = "visitas"

    id_visita = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    id_trabajador = Column(String, ForeignKey('trabajadores.id_trabajador'))
    id_cuota = Column(String, ForeignKey('cuotas.id_cuota'))
    fecha = Column(Date, nullable=False)
    resultado = Column(Enum(resultado_visita), nullable=False)
    observaciones = Column(String, nullable=True)
    trabajador = relationship('Trabajadores', back_populates='visitas')
    cuota = relationship('Cuotas', back_populates="visitas")
   