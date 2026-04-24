from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    notifications = Column(Boolean, default=True)
    role = Column(String, default="empleado")
    employee_code = Column(String, unique=True, index=True)

class AppAudit(Base):
    __tablename__ = "app_audits"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("app_tables.id", ondelete="CASCADE"))
    record_id = Column(Integer, ForeignKey("app_records.id", ondelete="CASCADE"))
    employee_code = Column(String)
    action = Column(String)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class AppTable(Base):
    __tablename__ = "app_tables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

    fields = relationship("AppField", back_populates="table", cascade="all, delete")
    records = relationship("AppRecord", back_populates="table", cascade="all, delete")

class AppField(Base):
    __tablename__ = "app_fields"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("app_tables.id", ondelete="CASCADE"))
    name = Column(String)  # ej. "Precio", "Cantidad"
    field_type = Column(String)  # ej. "text", "number", "select", "date"
    options = Column(String, nullable=True) # "A, B, C"
    order_index = Column(Integer, nullable=True)  # Para ordenar columnas

    table = relationship("AppTable", back_populates="fields")

class AppRecord(Base):
    __tablename__ = "app_records"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("app_tables.id", ondelete="CASCADE"))
    data = Column(JSON)  # Aquí se almacena la fila como un dict Ej. {"Precio": 100, "Cantidad": 50}

    table = relationship("AppTable", back_populates="records")
