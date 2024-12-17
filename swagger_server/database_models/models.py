from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Tabla Prospect
class Prospect(Base):
    __tablename__ = 'prospect'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)
    cedula = Column(String(10), unique=True, nullable=False)
    estado = Column(Integer, nullable=False)
    fecha_creacion = Column(Date, nullable=False)
    fecha_modificacion = Column(Date, nullable=True)

    user = relationship("User", back_populates="prospects")
    prospections = relationship("Prospection", back_populates="prospect")

    def to_dict(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "cedula": self.cedula,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion.strftime('%Y-%m-%d'),
            "fecha_modificacion": self.fecha_modificacion.strftime('%Y-%m-%d') if self.fecha_modificacion else None,
            "user": self.user.to_dict() if self.user else None
        }

# Tabla User
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    celular = Column(String(10), nullable=False)

    prospects = relationship("Prospect", back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "correo": self.correo,
            "celular": self.celular
        }

# Tabla Prospection
class Prospection(Base):
    __tablename__ = 'prospection'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_programa_academico = Column(Integer, nullable=False)
    id_prospect = Column(Integer, ForeignKey('prospect.id'), nullable=False)
    estado = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False)

    prospect = relationship("Prospect", back_populates="prospections")
    notes = relationship("Note", back_populates="prospection")
    emails = relationship("Email", back_populates="prospection")

    def to_dict(self):
        return {
            "id": self.id,
            "id_programa_academico": self.id_programa_academico,
            "id_prospect": self.id_prospect,
            "estado": self.estado,
            "fecha": self.fecha.strftime('%Y-%m-%d')
        }

# Tabla Note
class Note(Base):
    __tablename__ = 'note'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_prospection = Column(Integer, ForeignKey('prospection.id'), nullable=False)
    mensaje = Column(String(200), nullable=False)
    fecha = Column(Date, nullable=False)

    prospection = relationship("Prospection", back_populates="notes")

    def to_dict(self):
        return {
            "id": self.id,
            "id_prospection": self.id_prospection,
            "mensaje": self.mensaje,
            "fecha": self.fecha.strftime('%Y-%m-%d')
        }

# Tabla Email
class Email(Base):
    __tablename__ = 'email'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_prospection = Column(Integer, ForeignKey('prospection.id'), nullable=False)
    emisor = Column(String(50), nullable=False)
    mensaje = Column(String(200), nullable=False)
    fecha = Column(Date, nullable=False)

    prospection = relationship("Prospection", back_populates="emails")

    def to_dict(self):
        return {
            "id": self.id,
            "id_prospection": self.id_prospection,
            "emisor": self.emisor,
            "mensaje": self.mensaje,
            "fecha": self.fecha.strftime('%Y-%m-%d')
        }

# Tabla SalesAdvisor
class SalesAdvisor(Base):
    __tablename__ = 'sales_advisor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    celular = Column(String(10), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "correo": self.correo,
            "celular": self.celular
        }

class ProspectionSalesAdvisor(Base):
    __tablename__ = 'prospection_sales_advisor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_prospection = Column(Integer, ForeignKey('prospection.id'), nullable=False)
    id_sales_advisor = Column(Integer, ForeignKey('sales_advisor.id'), nullable=False)
    date = Column(Date, nullable=False)
    state = Column(Integer, nullable=False)

    prospection = relationship("Prospection", back_populates="sales_advisor_relationship")
    sales_advisor = relationship("SalesAdvisor", back_populates="prospections")

    def to_dict(self):
        return {
            "id": self.id,
            "id_prospection": self.id_prospection,
            "id_sales_advisor": self.id_sales_advisor,
            "date": self.date.strftime('%Y-%m-%d') if self.date else None,
            "state": self.state,
        }