from fastapi import FastAPI, Depends, Request, HTTPException, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import database, models, schemas
import uuid
from sqlalchemy.orm.attributes import flag_modified

app = FastAPI(title="MicroBase No-Code")

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Funciones Auxiliares (Seeders) ---
def init_db(db: Session):
    if db.query(models.AppTable).first() is None:
        # Inventario
        inv = models.AppTable(name="Inventario", description="Gestión de existencias")
        db.add(inv)
        db.commit()
        db.refresh(inv)
        db.add_all([
            models.AppField(table_id=inv.id, name="Nombre", field_type="text"),
            models.AppField(table_id=inv.id, name="Marca", field_type="text"),
            models.AppField(table_id=inv.id, name="COD", field_type="text"),
            models.AppField(table_id=inv.id, name="Unidad de Venta", field_type="text"),
            models.AppField(table_id=inv.id, name="Precio por Unidad", field_type="number"),
            models.AppField(table_id=inv.id, name="Cantidad", field_type="number")
        ])

        # Clientes
        cli = models.AppTable(name="Clientes", description="Base de clientes")
        db.add(cli)
        db.commit()
        db.refresh(cli)
        db.add_all([
            models.AppField(table_id=cli.id, name="Nombre", field_type="text"),
            models.AppField(table_id=cli.id, name="Teléfono", field_type="text"),
            models.AppField(table_id=cli.id, name="Email", field_type="text")
        ])

        # Empleados
        emp = models.AppTable(name="Empleados", description="Nómina y personal")
        db.add(emp)
        db.commit()
        db.refresh(emp)
        db.add_all([
            models.AppField(table_id=emp.id, name="Nombre Completo", field_type="text"),
            models.AppField(table_id=emp.id, name="Rol", field_type="select", options="manager, empleado"),
            models.AppField(table_id=emp.id, name="Salario", field_type="number")
        ])

        # Proveedores
        prov = models.AppTable(name="Proveedores", description="Gestión de suministradores")
        db.add(prov)
        db.commit()
        db.refresh(prov)
        db.add_all([
            models.AppField(table_id=prov.id, name="Nombre de Empresa", field_type="text"),
            models.AppField(table_id=prov.id, name="Contacto", field_type="text"),
            models.AppField(table_id=prov.id, name="RUC / NIT", field_type="text"),
            models.AppField(table_id=prov.id, name="Categoría", field_type="select", options="Alimentos, Bebidas, Embalaje, Otros")
        ])
        
        db.commit()

# Evento de inicio
@app.on_event("startup")
def on_startup():
    db = database.SessionLocal()
    init_db(db)
    db.close()

def get_current_user(request: Request, db: Session):
    token = request.cookies.get("auth_token")
    if not token:
        return None
    return db.query(models.User).filter(models.User.email == token).first()

# --- Vistas Frontend ---
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home_redirect(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request, db: Session = Depends(database.get_db)):
    if get_current_user(request, db):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse, include_in_schema=False)
async def register_page(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    # Si hay usuario y es empleado, no puede ver el registro
    if user and user.role not in ["admin", "manager"]:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("register.html", {"request": request, "user": user})

@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_page(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/tables-view", response_class=HTMLResponse, include_in_schema=False)
async def tables_view(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    tables = db.query(models.AppTable).all()
    return templates.TemplateResponse("index.html", {"request": request, "tables": tables, "user": user})

@app.get("/audits-view", response_class=HTMLResponse, include_in_schema=False)
async def audits_view(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    audits = db.query(models.AppAudit).order_by(models.AppAudit.id.desc()).limit(100).all()
    return templates.TemplateResponse("audits.html", {
        "request": request, 
        "user": user, 
        "audits": audits
    })

@app.get("/settings", response_class=HTMLResponse, include_in_schema=False)
async def settings_page(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("settings.html", {"request": request, "user": user})

@app.get("/create-table", response_class=HTMLResponse, include_in_schema=False)
async def create_table_page(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "manager"]:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    tables = db.query(models.AppTable).all()
    return templates.TemplateResponse("create_table.html", {"request": request, "user": user, "tables": tables})

@app.get("/ticket/{audit_id}", response_class=HTMLResponse, include_in_schema=False)
async def ticket_view(audit_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    audit = db.query(models.AppAudit).filter(models.AppAudit.id == audit_id).first()
    if not audit or not audit.details:
        raise HTTPException(status_code=404, detail="Ticket no encontrado o no tiene detalles.")
        
    return templates.TemplateResponse("ticket.html", {"request": request, "user": user, "audit": audit})

# --- APIs ---
@app.post("/auth/check-email", tags=["auth"])
def check_email(payload: schemas.EmailCheck, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    return {"exists": user is not None}

@app.post("/auth/register", response_model=schemas.UserResponse, tags=["auth"])
def api_register(payload: schemas.UserCreate, request: Request, response: Response, db: Session = Depends(database.get_db)):
    current_user = get_current_user(request, db)
    
    # Validaciones RBAC
    if current_user:
        if current_user.role == "manager" and payload.role in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="Un Manager solo puede crear cuentas de Empleados.")
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para registrar usuarios.")
            
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    nuevo_codigo = "EMP-" + str(uuid.uuid4())[:6].upper()
    
    new_user = models.User(
        email=payload.email, 
        full_name=payload.full_name, 
        hashed_password=payload.password,
        role=payload.role,
        employee_code=nuevo_codigo
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Solo establecer cookie y loguear automáticamente si NO hay nadie logueado (registro inicial)
    if not current_user:
        response.set_cookie(key="auth_token", value=new_user.email, httponly=True)
        
    return new_user

@app.post("/auth/login", tags=["auth"])
def api_login(payload: schemas.UserLogin, response: Response, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or user.hashed_password != payload.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    response.set_cookie(key="auth_token", value=user.email, httponly=True)
    return {"ok": True}

@app.post("/auth/logout", tags=["auth"])
def api_logout(response: Response):
    response.delete_cookie(key="auth_token")
    return {"ok": True}


@app.get("/tables", response_model=list[schemas.AppTable], tags=["tables"])
def api_get_tables(db: Session = Depends(database.get_db)):
    return db.query(models.AppTable).all()

@app.get("/tables/{table_id}", response_model=schemas.AppTable, tags=["tables"])
def api_get_table(table_id: int, db: Session = Depends(database.get_db)):
    table = db.query(models.AppTable).filter(models.AppTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    # Ordenar campos por order_index, fallback a id
    table.fields = sorted(table.fields, key=lambda f: (f.order_index if f.order_index is not None else f.id))
    return table

@app.post("/api/tables/full", response_model=schemas.AppTable, tags=["tables"])
def api_create_table_full(payload: schemas.AppTableCreateFull, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear tablas.")
    
    # Crear la tabla
    new_table = models.AppTable(name=payload.name, description=payload.description)
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    
    # Separar campos auto-generados para ponerlos al inicio
    auto_fields = []
    normal_fields = []
    for field in payload.fields:
        if field.name.upper() in ["COD", "ID"]:
            auto_fields.append(field)
        else:
            normal_fields.append(field)
            
    reordered_fields = auto_fields + normal_fields

    # Crear los campos con su order_index preservado
    for idx, field in enumerate(reordered_fields):
        db_field = models.AppField(
            name=field.name,
            field_type=field.field_type,
            options=field.options,
            order_index=idx,
            table_id=new_table.id
        )
        db.add(db_field)

    db.commit()
    db.refresh(new_table)
    return new_table

@app.put("/tables/{table_id}/reorder-fields", tags=["tables"])
def api_reorder_fields(table_id: int, payload: schemas.ReorderFieldsPayload, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para reordenar columnas.")
    for item in payload.fields:
        db.query(models.AppField).filter(models.AppField.id == item.id).update({"order_index": item.order_index})
    db.commit()
    return {"ok": True}

@app.delete("/tables/{table_id}", tags=["tables"])
def api_delete_table(table_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar la tabla.")
    
    table = db.query(models.AppTable).filter(models.AppTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
        
    db.query(models.AppField).filter(models.AppField.table_id == table_id).delete()
    db.query(models.AppRecord).filter(models.AppRecord.table_id == table_id).delete()
    db.delete(table)
    db.commit()
    return {"ok": True}

@app.post("/tables/{table_id}/fields", response_model=schemas.AppField, tags=["tables"])
def api_add_field(table_id: int, field: schemas.AppFieldCreate, db: Session = Depends(database.get_db)):
    current_fields = db.query(models.AppField).filter(models.AppField.table_id == table_id).order_by(models.AppField.order_index).all()
    
    target_index = field.order_index
    if target_index is None:
        target_index = len(current_fields)
        
    max_auto_idx = -1
    for f in current_fields:
        if f.name.upper() in ["COD", "ID"]:
            if f.order_index is not None and f.order_index > max_auto_idx:
                max_auto_idx = f.order_index
                
    if field.name.upper() not in ["COD", "ID"]:
        if target_index <= max_auto_idx:
            target_index = max_auto_idx + 1
    else:
        target_index = 0

    for f in current_fields:
        if f.order_index is not None and f.order_index >= target_index:
            f.order_index += 1

    db_field = models.AppField(
        name=field.name,
        field_type=field.field_type,
        options=field.options,
        order_index=target_index,
        table_id=table_id
    )
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field

@app.delete("/fields/{field_id}", tags=["tables"])
def api_delete_field(field_id: int, db: Session = Depends(database.get_db)):
    db_field = db.query(models.AppField).filter(models.AppField.id == field_id).first()
    if db_field:
        db.delete(db_field)
        db.commit()
        return {"ok": True}
    return {"ok": False}

@app.put("/fields/{field_id}", response_model=schemas.AppField, tags=["tables"])
def api_update_field(field_id: int, field: schemas.AppFieldCreate, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar columnas.")
    db_field = db.query(models.AppField).filter(models.AppField.id == field_id).first()
    if not db_field:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    db_field.name = field.name
    db_field.field_type = field.field_type
    db_field.options = field.options
    db.commit()
    db.refresh(db_field)
    return db_field

@app.post("/records/{table_id}", response_model=schemas.AppRecord, tags=["records"])
def api_add_record(table_id: int, record: schemas.AppRecordCreate, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Permisos insuficientes para crear registros manually")
    
    # Trabajar con una copia explícita del dict para evitar problemas con Pydantic v2
    data_copy = dict(record.data)

    # Consultar los campos de la tabla para saber cuáles son auto-generados
    fields = db.query(models.AppField).filter(models.AppField.table_id == table_id).all()

    # Auto-generate COD
    cod_field = next((f for f in fields if f.name.upper() == 'COD'), None)
    if cod_field and not data_copy.get(cod_field.name):
        data_copy[cod_field.name] = "COD-" + str(uuid.uuid4())[:8].upper()

    # Auto-generate ID
    id_field = next((f for f in fields if f.name.upper() == 'ID'), None)
    if id_field and not data_copy.get(id_field.name):
        data_copy[id_field.name] = str(uuid.uuid4())[:8].upper()

    db_record = models.AppRecord(data=data_copy, table_id=table_id)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.delete("/records/{record_id}", tags=["records"])
def api_delete_record(record_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Permisos insuficientes para eliminar registros")
    db_record = db.query(models.AppRecord).filter(models.AppRecord.id == record_id).first()
    if db_record:
        db.delete(db_record)
        db.commit()
        return {"ok": True}
    return {"ok": False}

@app.put("/records/{record_id}", response_model=schemas.AppRecord, tags=["records"])
def api_update_record(record_id: int, record: schemas.AppRecordCreate, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Permisos insuficientes para editar la tabla manualmente")

    db_record = db.query(models.AppRecord).filter(models.AppRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db_record.data = record.data
    
    # Audit trail
    audit = models.AppAudit(
        table_id=db_record.table_id,
        record_id=db_record.id,
        employee_code=user.employee_code,
        action="Updated record"
    )
    db.add(audit)
    
    db.commit()
    db.refresh(db_record)
    return db_record

@app.post("/inventory/movement", tags=["inventory"])
def api_inventory_movement(payload: schemas.MovementPayload, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")

    # RBAC para el Cajero y Bodeguero
    if payload.type == "Venta" and user.role == 'bodeguero':
        raise HTTPException(status_code=403, detail="Bodegueros no pueden procesar salidas de venta")
    if payload.type == "Compra" and user.role not in ['admin', 'manager', 'bodeguero']:
        raise HTTPException(status_code=403, detail="Los cajeros no tienen permiso para inyectar stock")

    for item in payload.items:
        db_record = db.query(models.AppRecord).filter(models.AppRecord.id == item.record_id).first()
        if not db_record: continue

        raw_qty = db_record.data.get('Cantidad', 0)
        try:
            current_qty = float(raw_qty) if str(raw_qty).strip() != "" else 0.0
        except (ValueError, TypeError):
            current_qty = 0.0
        if payload.type == "Venta":
            db_record.data['Cantidad'] = current_qty - item.quantity_change
        else:
            db_record.data['Cantidad'] = current_qty + item.quantity_change
        
        flag_modified(db_record, "data")
        
    first_item = db.query(models.AppRecord).filter(models.AppRecord.id == payload.items[0].record_id).first() if payload.items else None
    
    label_sujeto = "Proveedor" if payload.type == "Compra" else "Cliente"
    audit = models.AppAudit(
        table_id=first_item.table_id if first_item else None,
        record_id=None,
        employee_code=user.employee_code,
        action=f"{payload.type} | {label_sujeto}: {payload.client_name or 'Consumidor Final'} | Total: ${payload.total:.2f}",
        details=payload.model_dump()
    )
    db.add(audit)
        
    db.commit()
    db.refresh(audit)
    return {"ok": True, "processed": len(payload.items), "audit_id": audit.id}

@app.get("/api/clients/suggest", tags=["inventory"])
def api_clients_suggest(db: Session = Depends(database.get_db)):
    t = db.query(models.AppTable).filter(models.AppTable.name.ilike('cliente%')).first()
    names = []
    if t:
        for r in t.records:
            # Intentar buscar en 'Nombre' o 'Nombre de Empresa'
            n = r.data.get('Nombre') or r.data.get('Nombre Completo')
            if n and n not in names:
                names.append(n)
    return names

@app.get("/api/suppliers/suggest", tags=["inventory"])
def api_suppliers_suggest(db: Session = Depends(database.get_db)):
    t = db.query(models.AppTable).filter(models.AppTable.name.ilike('proveedor%')).first()
    names = []
    if t:
        for r in t.records:
            n = r.data.get('Nombre de Empresa') or r.data.get('Nombre')
            if n and n not in names:
                names.append(n)
    return names

@app.get("/api/audits", tags=["audit"])
def api_get_audits(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    audits = db.query(models.AppAudit).order_by(models.AppAudit.id.desc()).limit(100).all()
    result = []
    for a in audits:
        result.append({
            "id": a.id,
            "employee_code": a.employee_code,
            "action": a.action,
            "timestamp": a.timestamp.isoformat() if hasattr(a, 'timestamp') and a.timestamp else "N/A"
        })
    return result
