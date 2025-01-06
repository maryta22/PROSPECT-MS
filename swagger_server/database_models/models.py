from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Table: StateProspection
class StateProspection(Base):
    __tablename__ = 'state_prospection'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(50), nullable=False)
    state = Column(Integer, nullable=False)

    # Relación con StateProspectionProspection
    prospection_states = relationship(
        'StateProspectionProspection',
        back_populates='state_prospection',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "state": self.state
        }

# Table: User
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(10), nullable=False)

    prospects = relationship("Prospect", back_populates="user")
    sales_advisors = relationship("SalesAdvisor", back_populates="user")
    administrators = relationship("Administrator", back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone
        }

# Table: Administrator
class Administrator(Base):
    __tablename__ = 'administrator'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)
    state = Column(Integer, nullable=False)
    creation_date = Column(Date, nullable=False)
    modification_date = Column(Date, nullable=True)

    user = relationship("User", back_populates="administrators")

    def to_dict(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "state": self.state,
            "creation_date": self.creation_date.strftime('%Y-%m-%d'),
            "modification_date": self.modification_date.strftime('%Y-%m-%d') if self.modification_date else None
        }

# Table: SalesAdvisor
class SalesAdvisor(Base):
    __tablename__ = 'sales_advisor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)
    state = Column(Integer, nullable=False)

    user = relationship("User", back_populates="sales_advisors")
    prospections = relationship("ProspectionSalesAdvisor", back_populates="sales_advisor")

    def to_dict(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "state": self.state,
            "user": self.user.to_dict() if self.user else None
        }

# Table: AcademicProgram
class AcademicProgram(Base):
    __tablename__ = 'academic_program'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    state = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "state": self.state
        }

# Table: Prospect
class Prospect(Base):
    __tablename__ = 'prospect'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)
    id_number = Column(String(10), unique=True, nullable=False)
    state = Column(Integer, nullable=False)
    creation_date = Column(Date, nullable=False)
    modification_date = Column(Date, nullable=True)
    company = Column(String(255), nullable=True)
    id_city = Column(Integer, ForeignKey('city.id'), nullable=True)
    degree = Column(String(255), nullable=True)

    city = relationship("City", back_populates="prospects")
    user = relationship("User", back_populates="prospects")
    prospections = relationship("Prospection", back_populates="prospect")

    def to_dict(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "id_number": self.id_number,
            "state": self.state,
            "creation_date": self.creation_date,
            "modification_date": self.modification_date,
            "company": self.company,
            "city": self.city.to_dict() if self.city else None,
            "degree": self.degree,
            "user": self.user.to_dict() if self.user else None
        }

# Table: Prospection
class Prospection(Base):
    __tablename__ = 'prospection'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_academic_program = Column(Integer, ForeignKey('academic_program.id'), nullable=False)
    id_prospect = Column(Integer, ForeignKey('prospect.id'), nullable=False)
    date = Column(Date, nullable=False)
    state = Column(Integer, nullable=False)
    channel = Column(String(255), nullable=True)  # Agregamos la columna channel

    prospect = relationship("Prospect", back_populates="prospections")
    academic_program = relationship("AcademicProgram")
    notes = relationship("Note", back_populates="prospection")
    sales_advisors = relationship("ProspectionSalesAdvisor", back_populates="prospection")
    emails = relationship("ProspectionEmail", back_populates="prospection")
    state_prospections = relationship(
        "StateProspectionProspection",  # Nombre del modelo relacionado
        back_populates="prospection",  # Nombre de la relación inversa en StateProspectionProspection
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "id_academic_program": self.id_academic_program,
            "id_prospect": self.id_prospect,
            "date": self.date.strftime('%Y-%m-%d') if self.date else None,
            "state": self.state,
            "channel": self.channel
        }

# Table: ProspectionSalesAdvisor
class ProspectionSalesAdvisor(Base):
    __tablename__ = 'prospection_sales_advisor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_sales_advisor = Column(Integer, ForeignKey('sales_advisor.id'), nullable=False)
    id_prospection = Column(Integer, ForeignKey('prospection.id'), nullable=False)
    state = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)

    sales_advisor = relationship("SalesAdvisor", back_populates="prospections")
    prospection = relationship("Prospection", back_populates="sales_advisors")

    def to_dict(self):
        return {
            "id": self.id,
            "id_sales_advisor": self.id_sales_advisor,
            "id_prospection": self.id_prospection,
            "state": self.state,
            "date": self.date.strftime('%Y-%m-%d') if self.date else None
        }

# Table: Note
class Note(Base):
    __tablename__ = 'note'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_prospection = Column(Integer, ForeignKey('prospection.id'), nullable=False)
    message = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)

    prospection = relationship("Prospection", back_populates="notes")

    def to_dict(self):
        return {
            "id": self.id,
            "id_prospection": self.id_prospection,
            "message": self.message,
            "date": self.date.strftime('%Y-%m-%d') if self.date else None
        }

# Table: EmailType
class EmailType(Base):
    __tablename__ = 'email_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(String(200), nullable=False)
    state = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "state": self.state
        }

# Table: Email
class Email(Base):
    __tablename__ = 'email'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(String(50), nullable=False)
    message = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    platform_id = Column(String(50), nullable=True)
    id_email_type = Column(Integer, ForeignKey('email_type.id'), nullable=False)

    email_type = relationship("EmailType")

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "message": self.message,
            "date": self.date.strftime('%Y-%m-%d') if self.date else None,
            "platform_id": self.platform_id,
            "email_type": self.email_type.to_dict() if self.email_type else None
        }

# Table: ProspectionEmail
class ProspectionEmail(Base):
    __tablename__ = 'prospection_email'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_prospection = Column(Integer, ForeignKey('prospection.id'), nullable=False)
    id_email = Column(Integer, ForeignKey('email.id'), nullable=False)

    prospection = relationship("Prospection", back_populates="emails")
    email = relationship("Email")

    def to_dict(self):
        return {
            "id": self.id,
            "id_prospection": self.id_prospection,
            "id_email": self.id_email,
            "email": self.email.to_dict() if self.email else None
        }

class StateProspectionProspection(Base):
    __tablename__ = 'state_prospection_prospection'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_prospection = Column(Integer, ForeignKey('prospection.id'), nullable=False)
    id_state_prospection = Column(Integer, ForeignKey('state_prospection.id'), nullable=False)
    date = Column(Date, nullable=False)
    state = Column(Integer, nullable=False)

    # Relaciones
    prospection = relationship('Prospection', back_populates='state_prospections')
    state_prospection = relationship('StateProspection', back_populates='prospection_states')

    def to_dict(self):
        """Convierte el modelo en un diccionario para facilitar la serialización."""
        return {
            "id": self.id,
            "id_prospection": self.id_prospection,
            "id_state_prospection": self.id_state_prospection,
            "date": self.date.strftime('%Y-%m-%d') if self.date else None,
            "state": self.state
        }

class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    # Relación con Prospect
    prospects = relationship("Prospect", back_populates="city")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }