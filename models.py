from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, unique=True, index=True)
    setup_completed = Column(Boolean, default=False, server_default="false")

    users = relationship("User", back_populates="business", cascade="all, delete")
    tables = relationship("AppTable", back_populates="business", cascade="all, delete")
    audits = relationship("AppAudit", back_populates="business", cascade="all, delete")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    notifications = Column(Boolean, default=True)
    role = Column(String, default="empleado") # admin, manager, empleado
    employee_code = Column(String, unique=True, index=True)
    cedula = Column(String, unique=True, index=True, nullable=True)
    status = Column(String, default="pending") # active, pending

    business = relationship("Business", back_populates="users")

class AppAudit(Base):
    __tablename__ = "app_audits"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=True)
    table_id = Column(Integer, ForeignKey("app_tables.id", ondelete="CASCADE"), nullable=True)
    record_id = Column(Integer, ForeignKey("app_records.id", ondelete="CASCADE"), nullable=True)
    employee_code = Column(String)
    action = Column(String)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="active", server_default="active")
    modification_notes = Column(String, nullable=True)
    proposed_details = Column(JSON, nullable=True)

    business = relationship("Business", back_populates="audits")

class AppTable(Base):
    __tablename__ = "app_tables"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

    business = relationship("Business", back_populates="tables")
    fields = relationship("AppField", back_populates="table", cascade="all, delete")
    records = relationship("AppRecord", back_populates="table", cascade="all, delete")

class AppField(Base):
    __tablename__ = "app_fields"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("app_tables.id", ondelete="CASCADE"))
    name = Column(String)  # ej. "Precio", "Cantidad"
    field_type = Column(String)  # ej. "text", "number", "select", "date"
    options = Column(String, nullable=True) # "A, B, C"
    order_index = Column(Integer, nullable=True)

    table = relationship("AppTable", back_populates="fields")

class AppRecord(Base):
    __tablename__ = "app_records"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("app_tables.id", ondelete="CASCADE"))
    data = Column(JSON)

    table = relationship("AppTable", back_populates="records")
