from pydantic import BaseModel, field_validator
from typing import List, Optional, Any, Dict

class UserBase(BaseModel):
    email: str
    full_name: str
    notifications: Optional[bool] = True

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        if not isinstance(v, str) or "@" not in v:
            raise ValueError('El correo debe llevar "@"')
        return v

class UserCreate(UserBase):
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class EmailCheck(BaseModel):
    email: str

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        if not isinstance(v, str) or "@" not in v:
            raise ValueError('El correo debe llevar "@"')
        return v

class UserResponse(UserBase):
    id: int
    role: str
    employee_code: Optional[str] = None

    class Config:
        from_attributes = True

class AppFieldBase(BaseModel):
    name: str
    field_type: str
    options: Optional[str] = None
    order_index: Optional[int] = None

class AppFieldCreate(AppFieldBase):
    pass

class AppField(AppFieldBase):
    id: int
    table_id: int
    
    class Config:
        from_attributes = True

class AppRecordBase(BaseModel):
    data: Dict[str, Any]

class AppRecordCreate(AppRecordBase):
    pass

class AppRecord(AppRecordBase):
    id: int
    table_id: int

    class Config:
        from_attributes = True

class MovementItem(BaseModel):
    record_id: int
    quantity_change: float

class MovementPayload(BaseModel):
    type: str # 'Venta' or 'Compra'
    client_name: Optional[str] = None
    subtotal: float = 0.0
    iva: float = 0.0
    total: float = 0.0
    items: List[MovementItem]

class AppTableBase(BaseModel):
    name: str
    description: Optional[str] = None

class AppTableCreate(AppTableBase):
    pass

class AppTableCreateFull(AppTableBase):
    fields: List[AppFieldCreate]

class AppTable(AppTableBase):
    id: int
    fields: List[AppField] = []
    records: List[AppRecord] = []

    class Config:
        from_attributes = True

class FieldOrderItem(BaseModel):
    id: int
    order_index: int

class ReorderFieldsPayload(BaseModel):
    fields: List[FieldOrderItem]
