from fastapi import FastAPI, Depends, Request, HTTPException, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import cast, String, or_
import database, models, schemas
import uuid
from sqlalchemy.orm.attributes import flag_modified
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_status_email(to_email: str, name: str, status: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_user or not smtp_password:
        print("SMTP no configurado. Saltando envío de correo.")
        return False, "SMTP credentials missing"

    subject = ""
    body = ""
    
    if status == "approved":
        subject = "Tu cuenta ha sido aprobada - MicroBase No-Code"
        body = f"Hola {name},\n\nTu cuenta ha sido aprobada por el administrador. Ahora puedes iniciar sesión en el sistema.\n\nSaludos,\nEl equipo de MicroBase No-Code"
    elif status == "rejected":
        subject = "Tu solicitud de cuenta ha sido rechazada - MicroBase No-Code"
        body = f"Hola {name},\n\nLamentamos informarte que tu solicitud de cuenta ha sido rechazada por el administrador.\n\nSaludos,\nEl equipo de MicroBase No-Code"
    elif status == "deleted":
        subject = "Tu cuenta ha sido eliminada - MicroBase No-Code"
        body = f"Hola {name},\n\nTe informamos que tu cuenta ha sido eliminada del sistema por el administrador.\n\nSaludos,\nEl equipo de MicroBase No-Code"
    elif status == "business_created":
        subject = "¡Bienvenido! Tu Negocio ha sido Creado - MicroBase No-Code"
        body = f"Hola {name},\n\n¡Felicidades! Tu negocio ha sido creado exitosamente en MicroBase No-Code.\nYa puedes iniciar sesión en el sistema para comenzar a administrarlo.\n\nSaludos,\nEl equipo de MicroBase No-Code"
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Correo enviado exitosamente a {to_email}")
        return True, ""
    except Exception as e:
        print(f"Error al enviar correo a {to_email}: {e}")
        return False, str(e)

app = FastAPI(title="MicroBase No-Code")

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def init_db(db: Session, business_id: int):
    if db.query(models.AppTable).filter_by(business_id=business_id).first() is None:
        # Inventario
        inv = models.AppTable(name="Inventario", description="Gestión de existencias", business_id=business_id)
        db.add(inv)
        db.commit()
        db.refresh(inv)
        db.add_all([
            models.AppField(table_id=inv.id, name="Nombre", field_type="text", order_index=0),
            models.AppField(table_id=inv.id, name="Marca", field_type="text", order_index=1),
            models.AppField(table_id=inv.id, name="COD", field_type="text", order_index=2),
            models.AppField(table_id=inv.id, name="Unidad de Venta", field_type="text", order_index=3),
            models.AppField(table_id=inv.id, name="Precio por Unidad", field_type="number_decimal", order_index=4),
            models.AppField(table_id=inv.id, name="Cantidad", field_type="number_int", order_index=5)
        ])

        # Clientes
        cli = models.AppTable(name="Clientes", description="Base de clientes", business_id=business_id)
        db.add(cli)
        db.commit()
        db.refresh(cli)
        db.add_all([
            models.AppField(table_id=cli.id, name="Nombre", field_type="text", order_index=0),
            models.AppField(table_id=cli.id, name="Cédula", field_type="text", order_index=1),
            models.AppField(table_id=cli.id, name="Teléfono", field_type="text", order_index=2),
            models.AppField(table_id=cli.id, name="Email", field_type="text", order_index=3)
        ])

        # Empleados
        emp = models.AppTable(name="Empleados", description="Nómina y personal", business_id=business_id)
        db.add(emp)
        db.commit()
        db.refresh(emp)
        db.add_all([
            models.AppField(table_id=emp.id, name="Nombre Completo", field_type="text", order_index=0),
            models.AppField(table_id=emp.id, name="Rol", field_type="select", options="manager, empleado", order_index=1),
            models.AppField(table_id=emp.id, name="Salario", field_type="number_decimal", order_index=2)
        ])

        # Proveedores
        prov = models.AppTable(name="Proveedores", description="Gestión de suministradores", business_id=business_id)
        db.add(prov)
        db.commit()
        db.refresh(prov)
        db.add_all([
            models.AppField(table_id=prov.id, name="Nombre de Empresa", field_type="text", order_index=0),
            models.AppField(table_id=prov.id, name="Contacto", field_type="text", order_index=1),
            models.AppField(table_id=prov.id, name="RUC / NIT", field_type="text", order_index=2),
            models.AppField(table_id=prov.id, name="Categoría", field_type="select", options="Alimentos, Bebidas, Embalaje, Otros", order_index=3)
        ])
        
        db.commit()

# Evento de inicio
@app.on_event("startup")
def on_startup():
    pass

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
        return templates.TemplateResponse("welcome.html", {"request": request})
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
    
    setup_completed = False
    if user.business:
        setup_completed = user.business.setup_completed or False
        
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "setup_completed": setup_completed
    })

@app.get("/staff", response_class=HTMLResponse, include_in_schema=False)
async def staff_page(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    if user.role != 'admin':
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("staff.html", {"request": request, "user": user})

@app.get("/tables-view", response_class=HTMLResponse, include_in_schema=False)
async def tables_view(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    tables = db.query(models.AppTable).filter(models.AppTable.business_id == user.business_id).all()
    return templates.TemplateResponse("index.html", {"request": request, "tables": tables, "user": user})

@app.get("/audits-view", response_class=HTMLResponse, include_in_schema=False)
async def audits_view(request: Request, q: str = None, tab: str = "active", limit: int = 25, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    query = db.query(models.AppAudit).filter(models.AppAudit.business_id == user.business_id)
    
    # Filter by tab
    if tab == "pending":
        query = query.filter(models.AppAudit.status == "pending_change")
    elif tab == "annulled":
        query = query.filter(models.AppAudit.status == "annulled")
    else:
        query = query.filter(or_(
            models.AppAudit.status == "active",
            models.AppAudit.status == "modified",
            models.AppAudit.status == None
        ))
        
    if q:
        q_clean = q.strip()
        ticket_id = None
        if q_clean.lower().startswith("tkt-"):
            try:
                ticket_id = int(q_clean[4:])
            except ValueError:
                pass
        else:
            try:
                ticket_id = int(q_clean)
            except ValueError:
                pass
                
        filters = [
            models.AppAudit.employee_code.ilike(f"%{q_clean}%"),
            models.AppAudit.action.ilike(f"%{q_clean}%"),
            cast(models.AppAudit.timestamp, String).ilike(f"%{q_clean}%")
        ]
        
        if ticket_id is not None:
            filters.append(models.AppAudit.id == ticket_id)
            
        query = query.filter(or_(*filters))
        
    total_count = query.count()
    audits = query.order_by(models.AppAudit.id.desc()).limit(limit).all()
    has_more = total_count > len(audits)
    
    pending_count = db.query(models.AppAudit).filter(
        models.AppAudit.business_id == user.business_id,
        models.AppAudit.status == "pending_change"
    ).count()
    
    return templates.TemplateResponse("audits.html", {
        "request": request, 
        "user": user, 
        "audits": audits,
        "q": q or "",
        "tab": tab,
        "pending_count": pending_count,
        "limit": limit,
        "has_more": has_more,
        "total_count": total_count
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
    tables = db.query(models.AppTable).filter(models.AppTable.business_id == user.business_id).all()
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

@app.post("/auth/check-registration", tags=["auth"])
def check_registration(payload: schemas.RegistrationCheck, db: Session = Depends(database.get_db)):
    email_exists = db.query(models.User).filter(models.User.email == payload.email).first() is not None
    cedula_exists = db.query(models.User).filter(models.User.cedula == payload.cedula).first() is not None
    return {"email_exists": email_exists, "cedula_exists": cedula_exists}

@app.post("/auth/register", response_model=schemas.UserResponse, tags=["auth"])
def api_register(payload: schemas.UserRegister, request: Request, response: Response, db: Session = Depends(database.get_db)):
    # Validate cedula is required
    if not payload.cedula:
        raise HTTPException(status_code=400, detail="La cédula es obligatoria.")

    existing_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
        
    existing_cedula = db.query(models.User).filter(models.User.cedula == payload.cedula).first()
    if existing_cedula:
        raise HTTPException(status_code=400, detail="Cédula/RUC ya registrado")

    nuevo_codigo = "EMP-" + str(uuid.uuid4())[:6].upper()

    # Flow 1: Create Business (Owner)
    if payload.business_name:
        existing_business = db.query(models.Business).filter(models.Business.code == payload.business_code).first()
        if existing_business:
            raise HTTPException(status_code=400, detail="El código de negocio ya está en uso. Por favor, elige otro.")
        
        new_business = models.Business(name=payload.business_name, code=payload.business_code)
        db.add(new_business)
        db.commit()
        db.refresh(new_business)
        
        new_user = models.User(
            email=payload.email, 
            full_name=payload.full_name, 
            hashed_password=payload.password,
            role="admin",
            employee_code=nuevo_codigo,
            cedula=payload.cedula,
            business_id=new_business.id,
            status="active"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Initialize default tables for this new business
        init_db(db, new_business.id)
        
        # Enviar correo de creación de negocio
        send_status_email(new_user.email, new_user.full_name, "business_created")
        
        # Login automatically since they are the owner
        response.set_cookie(key="auth_token", value=new_user.email, httponly=True)
        return new_user

    # Flow 2: Join Business (Employee)
    else:
        business = db.query(models.Business).filter(models.Business.code == payload.business_code).first()
        if not business:
            raise HTTPException(status_code=404, detail="No se encontró ningún negocio con ese código.")
            
        new_user = models.User(
            email=payload.email, 
            full_name=payload.full_name, 
            hashed_password=payload.password,
            role="empleado", # Will be assigned by admin later
            employee_code=nuevo_codigo,
            cedula=payload.cedula,
            business_id=business.id,
            status="pending"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user

@app.post("/auth/login", tags=["auth"])
def api_login(payload: schemas.UserLogin, response: Response, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or user.hashed_password != payload.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if user.status == "pending":
        raise HTTPException(status_code=403, detail="Tu cuenta aún está pendiente de aprobación por el Administrador.")
        
    if user.status == "fired":
        raise HTTPException(status_code=403, detail="Tu cuenta ha sido desactivada por la administración. Por favor contacta al administrador.")
        
    response.set_cookie(key="auth_token", value=user.email, httponly=True)
    return {"ok": True}

@app.post("/auth/logout", tags=["auth"])
def api_logout(response: Response):
    response.delete_cookie(key="auth_token")
    return {"ok": True}


@app.get("/tables", response_model=list[schemas.AppTable], tags=["tables"])
def api_get_tables(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user: raise HTTPException(status_code=401, detail="No autorizado")
    return db.query(models.AppTable).filter(models.AppTable.business_id == user.business_id).all()

@app.get("/tables/{table_id}", response_model=schemas.AppTable, tags=["tables"])
def api_get_table(table_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user: raise HTTPException(status_code=401, detail="No autorizado")
    table = db.query(models.AppTable).filter(models.AppTable.id == table_id, models.AppTable.business_id == user.business_id).first()
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
    
    # Auto-generar columnas requeridas si es Inventario manual
    if "inventario" in payload.name.lower():
        existing_names = [f.name.upper() for f in payload.fields]
        required_fields = [
            ("Nombre", "text"),
            ("COD", "text"),
            ("Precio por Unidad", "number_decimal"),
            ("Cantidad", "number_int")
        ]
        for r_name, r_type in required_fields:
            if r_name.upper() not in existing_names:
                payload.fields.append(schemas.AppFieldCreateFull(name=r_name, field_type=r_type))

    # Crear la tabla ligada al negocio
    new_table = models.AppTable(name=payload.name, description=payload.description, business_id=user.business_id)
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    
    # Separar campos auto-generados para ponerlos al inicio
    auto_fields = []
    normal_fields = []
    for field in payload.fields:
        if field.name.upper() in ["COD", "ID", "CÓDIGO"]:
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
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(db_record, "data")
    
    # Audit trail
    audit = models.AppAudit(
        business_id=user.business_id,
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

    # RBAC para el Cajero
    if payload.type == "Compra" and user.role not in ['admin', 'manager']:
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
    cedula_text = f" | Cédula/RUC: {payload.client_cedula}" if getattr(payload, "client_cedula", None) else ""
    audit = models.AppAudit(
        business_id=user.business_id,
        table_id=first_item.table_id if first_item else None,
        record_id=None,
        employee_code=user.employee_code,
        action=f"{payload.type} | {label_sujeto}: {payload.client_name or 'Consumidor Final'}{cedula_text} | Total: ${payload.total:.2f}",
        details=payload.model_dump()
    )
    db.add(audit)
        
    db.commit()
    db.refresh(audit)
    return {"ok": True, "processed": len(payload.items), "audit_id": audit.id}

@app.get("/api/clients/suggest", tags=["inventory"])
def api_clients_suggest(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user: return []
    t = db.query(models.AppTable).filter(models.AppTable.business_id == user.business_id, models.AppTable.name.ilike('cliente%')).first()
    results = []
    if t:
        for r in t.records:
            n = r.data.get('Nombre') or r.data.get('Nombre Completo')
            c = r.data.get('Cédula') or r.data.get('Cedula') or r.data.get('RUC') or r.data.get('Identificación') or ""
            if n or c:
                results.append({"name": n, "cedula": c})
    
    unique_results = []
    seen = set()
    for item in results:
        identifier = f"{item['name']}-{item['cedula']}"
        if identifier not in seen:
            seen.add(identifier)
            unique_results.append(item)
    return unique_results

@app.get("/api/suppliers/suggest", tags=["inventory"])
def api_suppliers_suggest(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user: return []
    t = db.query(models.AppTable).filter(models.AppTable.business_id == user.business_id, models.AppTable.name.ilike('proveedor%')).first()
    names = []
    if t:
        for r in t.records:
            n = r.data.get('Nombre de Empresa') or r.data.get('Nombre')
            if n and n not in names:
                names.append(n)
    return names

@app.get("/api/audits/suggest", tags=["audit"])
def api_audits_suggest(q: str = "", db: Session = Depends(database.get_db)):
    if not q or len(q.strip()) < 1:
        return []
    q_clean = q.strip()
    
    suggestions = []
    
    # 1. Operators matching q
    operators = db.query(models.AppAudit.employee_code).filter(
        models.AppAudit.employee_code.ilike(f"%{q_clean}%")
    ).distinct().limit(5).all()
    for op in operators:
        if op[0] and op[0] not in suggestions:
            suggestions.append(op[0])
            
    # 2. Actions matching q
    actions = db.query(models.AppAudit.action).filter(
        models.AppAudit.action.ilike(f"%{q_clean}%")
    ).distinct().limit(5).all()
    for act in actions:
        if act[0] and act[0] not in suggestions:
            suggestions.append(act[0])
            
    # 3. Tickets matching q
    ticket_id = None
    if q_clean.lower().startswith("tkt-"):
        try:
            ticket_id = int(q_clean[4:])
        except ValueError:
            pass
    else:
        try:
            ticket_id = int(q_clean)
        except ValueError:
            pass
            
    if ticket_id is not None:
        tickets = db.query(models.AppAudit.id).filter(
            cast(models.AppAudit.id, String).ilike(f"%{ticket_id}%")
        ).limit(5).all()
        for t in tickets:
            tkt_str = f"TKT-{t[0]}"
            if tkt_str not in suggestions:
                suggestions.append(tkt_str)
                
    return suggestions


@app.get("/api/audits", tags=["audit"])
def api_get_audits(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    audits = db.query(models.AppAudit).filter(models.AppAudit.business_id == user.business_id).order_by(models.AppAudit.id.desc()).limit(100).all()
    result = []
    for a in audits:
        result.append({
            "id": a.id,
            "employee_code": a.employee_code,
            "action": a.action,
            "timestamp": a.timestamp.isoformat() if hasattr(a, 'timestamp') and a.timestamp else "N/A"
        })
    return result

# --- Admin Personnel APIs ---
from pydantic import BaseModel
class ApproveUserPayload(BaseModel):
    role: str

@app.get("/api/users/pending", tags=["admin"])
def api_get_pending_users(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    pending = db.query(models.User).filter(
        models.User.business_id == user.business_id,
        models.User.status == "pending"
    ).all()
    
    return [{"id": u.id, "full_name": u.full_name, "email": u.email, "cedula": u.cedula, "status": u.status} for u in pending]

@app.get("/api/users/active", tags=["admin"])
def api_get_active_users(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    active = db.query(models.User).filter(
        models.User.business_id == user.business_id,
        models.User.status == "active"
    ).all()
    
    return [{"id": u.id, "full_name": u.full_name, "email": u.email, "role": u.role, "employee_code": u.employee_code} for u in active]

@app.post("/api/users/{user_id}/approve", tags=["admin"])
def api_approve_user(user_id: int, payload: ApproveUserPayload, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
        
    target_user = db.query(models.User).filter(models.User.id == user_id, models.User.business_id == user.business_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    target_user.status = "active"
    target_user.role = payload.role
    db.commit()
    
    success, error_msg = send_status_email(target_user.email, target_user.full_name, "approved")
    
    return {"ok": True, "email_sent": success, "email_error": error_msg if not success else None}

@app.post("/api/users/{user_id}/reject", tags=["admin"])
def api_reject_user(user_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
        
    target_user = db.query(models.User).filter(models.User.id == user_id, models.User.business_id == user.business_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    target_status = target_user.status
    target_email = target_user.email
    target_name = target_user.full_name
        
    if target_status == "pending":
        db.delete(target_user)
        action = "rejected"
    else:
        target_user.status = "fired"
        action = "deleted"
        
    db.commit()
    
    success, error_msg = send_status_email(target_email, target_name, action)
    
    return {"ok": True, "email_sent": success, "email_error": error_msg if not success else None}

@app.post("/api/audits/{audit_id}/request-modification", tags=["audit"])
def api_request_modification(audit_id: int, payload: schemas.RequestModificationPayload, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
        
    audit = db.query(models.AppAudit).filter(models.AppAudit.id == audit_id, models.AppAudit.business_id == user.business_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
        
    if audit.status in ["pending_change", "annulled"]:
        raise HTTPException(status_code=400, detail="Esta factura ya tiene una solicitud pendiente o está anulada")
        
    # Reconstruct proposed details
    orig_details = audit.details or {}
    orig_items = {item.get("record_id"): item for item in orig_details.get("items", [])}
    
    proposed_items = []
    new_total = 0.0
    for item in payload.items:
        orig_item = orig_items.get(item.record_id)
        if not orig_item:
            continue
        price = float(orig_item.get("price", 0.0))
        subtotal = float(item.quantity_change) * price
        new_total += subtotal
        proposed_items.append({
            "record_id": item.record_id,
            "quantity_change": float(item.quantity_change),
            "name": orig_item.get("name"),
            "price": price,
            "subtotal": subtotal
        })
        
    new_subtotal = new_total / 1.15
    new_iva = new_total - new_subtotal
    
    proposed_details = {
        "type": orig_details.get("type"),
        "client_name": orig_details.get("client_name"),
        "client_cedula": orig_details.get("client_cedula"),
        "subtotal": round(new_subtotal, 2),
        "iva": round(new_iva, 2),
        "total": round(new_total, 2),
        "items": proposed_items
    }
    
    audit.status = "pending_change"
    audit.modification_notes = payload.notes
    audit.proposed_details = proposed_details
    
    db.commit()
    return {"ok": True}

@app.post("/api/audits/{audit_id}/resolve-modification", tags=["audit"])
def api_resolve_modification(audit_id: int, payload: schemas.ResolveModificationPayload, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="No autorizado")
        
    audit = db.query(models.AppAudit).filter(models.AppAudit.id == audit_id, models.AppAudit.business_id == user.business_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
        
    if payload.action == "reject":
        audit.status = "active"
        audit.proposed_details = None
        db.commit()
        return {"ok": True}
        
    type_op = (audit.details or {}).get("type", "Venta")
    
    if payload.action == "approve":
        if not audit.proposed_details:
            raise HTTPException(status_code=400, detail="No hay detalles propuestos para aprobar")
            
        old_items = {item["record_id"]: item for item in (audit.details or {}).get("items", [])}
        new_items = {item["record_id"]: item for item in audit.proposed_details.get("items", [])}
        all_record_ids = set(list(old_items.keys()) + list(new_items.keys()))
        
        for record_id in all_record_ids:
            db_record = db.query(models.AppRecord).filter(models.AppRecord.id == record_id).first()
            if not db_record:
                continue
            
            raw_qty = db_record.data.get('Cantidad', 0)
            try:
                current_qty = float(raw_qty) if str(raw_qty).strip() != "" else 0.0
            except (ValueError, TypeError):
                current_qty = 0.0
                
            old_qty = float(old_items.get(record_id, {}).get("quantity_change", 0.0))
            new_qty = float(new_items.get(record_id, {}).get("quantity_change", 0.0))
            
            if type_op == "Venta":
                db_record.data['Cantidad'] = current_qty + (old_qty - new_qty)
            else:
                db_record.data['Cantidad'] = current_qty + (new_qty - old_qty)
                
            flag_modified(db_record, "data")
            
        audit.details = audit.proposed_details
        audit.proposed_details = None
        
        label_sujeto = "Proveedor" if type_op == "Compra" else "Cliente"
        client_name = audit.details.get("client_name") or "Consumidor Final"
        client_cedula = audit.details.get("client_cedula")
        cedula_text = f" | Cédula/RUC: {client_cedula}" if client_cedula else ""
        total_val = audit.details.get("total", 0.0)
        audit.action = f"{type_op} | {label_sujeto}: {client_name}{cedula_text} | Total: ${total_val:.2f}"
        audit.status = "modified"
        
        db.commit()
        return {"ok": True}
        
    elif payload.action == "annul":
        old_items = (audit.details or {}).get("items", [])
        for item in old_items:
            record_id = item.get("record_id")
            db_record = db.query(models.AppRecord).filter(models.AppRecord.id == record_id).first()
            if not db_record:
                continue
                
            raw_qty = db_record.data.get('Cantidad', 0)
            try:
                current_qty = float(raw_qty) if str(raw_qty).strip() != "" else 0.0
            except (ValueError, TypeError):
                current_qty = 0.0
                
            old_qty = float(item.get("quantity_change", 0.0))
            
            if type_op == "Venta":
                db_record.data['Cantidad'] = current_qty + old_qty
            else:
                db_record.data['Cantidad'] = current_qty - old_qty
                
            flag_modified(db_record, "data")
            
        audit.status = "annulled"
        audit.proposed_details = None
        db.commit()
        return {"ok": True}
        
    raise HTTPException(status_code=400, detail="Acción no válida")

@app.post("/api/audits/{audit_id}/direct-annul", tags=["audit"])
def api_direct_annul(audit_id: int, payload: schemas.DirectAnnulPayload, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="No autorizado")
        
    audit = db.query(models.AppAudit).filter(models.AppAudit.id == audit_id, models.AppAudit.business_id == user.business_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
        
    type_op = (audit.details or {}).get("type", "Venta")
    old_items = (audit.details or {}).get("items", [])
    
    for item in old_items:
        record_id = item.get("record_id")
        db_record = db.query(models.AppRecord).filter(models.AppRecord.id == record_id).first()
        if not db_record:
            continue
            
        raw_qty = db_record.data.get('Cantidad', 0)
        try:
            current_qty = float(raw_qty) if str(raw_qty).strip() != "" else 0.0
        except (ValueError, TypeError):
            current_qty = 0.0
            
        old_qty = float(item.get("quantity_change", 0.0))
        
        if type_op == "Venta":
            db_record.data['Cantidad'] = current_qty + old_qty
        else:
            db_record.data['Cantidad'] = current_qty - old_qty
            
        flag_modified(db_record, "data")
        
    audit.status = "annulled"
    audit.modification_notes = payload.notes
    audit.proposed_details = None
    db.commit()
    return {"ok": True}

@app.get("/api/audits/{audit_id}", tags=["audit"])
def api_get_audit(audit_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    audit = db.query(models.AppAudit).filter(models.AppAudit.id == audit_id, models.AppAudit.business_id == user.business_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return {
        "id": audit.id,
        "employee_code": audit.employee_code,
        "action": audit.action,
        "details": audit.details,
        "status": audit.status,
        "modification_notes": audit.modification_notes,
        "proposed_details": audit.proposed_details
    }

@app.get("/api/users/inactive", tags=["admin"])
def api_get_inactive_users(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    inactive = db.query(models.User).filter(
        models.User.business_id == user.business_id,
        models.User.status == "fired"
    ).all()
    
    return [{"id": u.id, "full_name": u.full_name, "email": u.email, "role": u.role, "employee_code": u.employee_code} for u in inactive]

@app.post("/api/users/{user_id}/rehire", tags=["admin"])
def api_rehire_user(user_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
        
    target_user = db.query(models.User).filter(models.User.id == user_id, models.User.business_id == user.business_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if target_user.status != "fired":
        raise HTTPException(status_code=400, detail="Este usuario no está de baja")
        
    target_user.status = "active"
    db.commit()
    
    success, error_msg = send_status_email(target_user.email, target_user.full_name, "approved")
    
    return {"ok": True, "email_sent": success, "email_error": error_msg if not success else None}

def setup_business_template(db: Session, business_id: int, template: str):
    tables_to_create = []
    
    if template == "restaurant":
        tables_to_create = [
            {
                "name": "Inventario",
                "description": "Gestión de existencias",
                "fields": [
                    {"name": "Nombre", "type": "text"},
                    {"name": "Marca", "type": "text"},
                    {"name": "COD", "type": "text"},
                    {"name": "Unidad de Venta", "type": "text"},
                    {"name": "Precio por Unidad", "type": "number_decimal"},
                    {"name": "Cantidad", "type": "number_int"}
                ]
            },
            {
                "name": "Menú",
                "description": "Catálogo de platillos y precios",
                "fields": [
                    {"name": "Nombre", "type": "text"},
                    {"name": "Descripción", "type": "text"},
                    {"name": "Precio", "type": "number_decimal"},
                    {"name": "Categoría", "type": "select", "options": "Entradas, Fuertes, Postres, Bebidas, Otros"}
                ]
            }
        ]
    elif template == "store":
        tables_to_create = [
            {
                "name": "Inventario",
                "description": "Gestión de existencias",
                "fields": [
                    {"name": "Nombre", "type": "text"},
                    {"name": "Marca", "type": "text"},
                    {"name": "COD", "type": "text"},
                    {"name": "Unidad de Venta", "type": "text"},
                    {"name": "Precio por Unidad", "type": "number_decimal"},
                    {"name": "Cantidad", "type": "number_int"}
                ]
            }
        ]
    elif template == "gym":
        tables_to_create = [
            {
                "name": "Inventario",
                "description": "Gestión de existencias",
                "fields": [
                    {"name": "Nombre", "type": "text"},
                    {"name": "Marca", "type": "text"},
                    {"name": "COD", "type": "text"},
                    {"name": "Unidad de Venta", "type": "text"},
                    {"name": "Precio por Unidad", "type": "number_decimal"},
                    {"name": "Cantidad", "type": "number_int"}
                ]
            },
            {
                "name": "Planes",
                "description": "Membresías del gimnasio",
                "fields": [
                    {"name": "Plan", "type": "text"},
                    {"name": "Costo", "type": "number_decimal"},
                    {"name": "Días", "type": "number_int"},
                    {"name": "Acceso", "type": "select", "options": "Pase Diario, Pase Mensual, Full Access"}
                ]
            }
        ]
    elif template == "liquor":
        tables_to_create = [
            {
                "name": "Inventario",
                "description": "Gestión de existencias",
                "fields": [
                    {"name": "Nombre", "type": "text"},
                    {"name": "Marca", "type": "text"},
                    {"name": "COD", "type": "text"},
                    {"name": "Unidad de Venta", "type": "text"},
                    {"name": "Precio por Unidad", "type": "number_decimal"},
                    {"name": "Cantidad", "type": "number_int"}
                ]
            }
        ]
        
    for t_info in tables_to_create:
        existing = db.query(models.AppTable).filter_by(business_id=business_id, name=t_info["name"]).first()
        if not existing:
            new_table = models.AppTable(name=t_info["name"], description=t_info["description"], business_id=business_id)
            db.add(new_table)
            db.commit()
            db.refresh(new_table)
            
            auto_fields = []
            normal_fields = []
            for f in t_info["fields"]:
                if f["name"].upper() in ["COD", "ID", "CÓDIGO"]:
                    auto_fields.append(f)
                else:
                    normal_fields.append(f)
            reordered_fields = auto_fields + normal_fields
            
            for idx, f in enumerate(reordered_fields):
                db_field = models.AppField(
                    table_id=new_table.id,
                    name=f["name"],
                    field_type=f["type"],
                    options=f.get("options"),
                    order_index=idx
                )
                db.add(db_field)
            db.commit()

@app.post("/api/business/setup-template", tags=["admin"])
def api_setup_business_template(payload: schemas.SetupTemplatePayload, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
        
    business = db.query(models.Business).filter(models.Business.id == user.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
        
    setup_business_template(db, business.id, payload.template)
    
    business.setup_completed = True
    db.commit()
    
    return {"ok": True}

@app.get("/api/dashboard/stats", tags=["admin"])
def api_get_dashboard_stats(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
        
    import datetime

    # UTC a Local (Ecuador UTC-5)
    tz_offset = datetime.timedelta(hours=5)
    local_now = datetime.datetime.utcnow() - tz_offset

    # Parsear filtros de fecha opcionales desde los query parameters
    start_date_str = request.query_params.get("start_date")
    end_date_str = request.query_params.get("end_date")
    
    filter_start = None
    filter_end = None
    if start_date_str:
        try:
            filter_start = datetime.datetime.strptime(start_date_str.strip(), "%Y-%m-%d")
        except ValueError:
            pass
    if end_date_str:
        try:
            filter_end = datetime.datetime.strptime(end_date_str.strip(), "%Y-%m-%d")
            # Ajustar al final del día local (23:59:59.999999)
            filter_end = filter_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        except ValueError:
            pass

    # Filtrar auditorías para KPIs (si hay fechas, limita el rango; si no, calcula acumulado histórico)
    kpi_query = db.query(models.AppAudit).filter(
        models.AppAudit.business_id == user.business_id, 
        models.AppAudit.status != "annulled"
    )
    if filter_start:
        kpi_query = kpi_query.filter(models.AppAudit.timestamp >= (filter_start + tz_offset))
    if filter_end:
        kpi_query = kpi_query.filter(models.AppAudit.timestamp <= (filter_end + tz_offset))
        
    audits = kpi_query.all()
    
    total_sales = 0.0
    total_purchases = 0.0
    for a in audits:
        if a.details:
            t_type = a.details.get("type")
            t_val = float(a.details.get("total", 0.0))
            if t_type == "Venta":
                total_sales += t_val
            elif t_type == "Compra":
                total_purchases += t_val
                
    gain_net = total_sales - total_purchases
    total_transactions = len(audits)
    
    low_stock_count = 0
    inv_table = db.query(models.AppTable).filter(models.AppTable.business_id == user.business_id, models.AppTable.name.ilike('inventario%')).first()
    if inv_table:
        for r in inv_table.records:
            qty_val = r.data.get("Cantidad", 0)
            try:
                qty = float(qty_val) if str(qty_val).strip() != "" else 0.0
            except (ValueError, TypeError):
                qty = 0.0
            if qty <= 3:
                low_stock_count += 1
                
    product_ids_str = request.query_params.get("products")
    product_ids = []
    if product_ids_str:
        product_ids = [int(pid.strip()) for pid in product_ids_str.split(",") if pid.strip().isdigit()]
        
    # Determinar el rango de fechas para el eje X del gráfico
    if filter_start:
        local_start = filter_start.date()
    else:
        local_start = (local_now - datetime.timedelta(days=6)).date()
        
    if filter_end:
        local_end = filter_end.date()
    else:
        local_end = local_now.date()
        
    # Limitar el rango máximo del gráfico a 62 días para protección de rendimiento
    if (local_end - local_start).days > 62:
        local_start = local_end - datetime.timedelta(days=62)
        
    if local_start > local_end:
        local_start = local_end
        
    # Generar la lista de días (eje X)
    delta = local_end - local_start
    days = [local_start + datetime.timedelta(days=i) for i in range(delta.days + 1)]
    chart_labels = [d.strftime("%d/%m") for d in days]
    
    # Obtener auditorías de ventas en el rango UTC correspondiente
    start_date_utc = datetime.datetime.combine(local_start, datetime.time.min) + tz_offset
    end_date_utc = datetime.datetime.combine(local_end, datetime.time.max) + tz_offset
    
    sales_audits = db.query(models.AppAudit).filter(
        models.AppAudit.business_id == user.business_id,
        models.AppAudit.status != "annulled",
        models.AppAudit.timestamp >= start_date_utc,
        models.AppAudit.timestamp <= end_date_utc
    ).order_by(models.AppAudit.timestamp.asc()).all()
    
    recent_sales = [a for a in sales_audits if a.details and a.details.get("type") == "Venta"]
    
    chart_datasets = []
    
    if product_ids:
        colors = ["#10b981", "#8b5cf6", "#3b82f6", "#f59e0b", "#ec4899", "#14b8a6"]
        for idx, pid in enumerate(product_ids):
            product_name = f"Prod #{pid}"
            
            p_record = db.query(models.AppRecord).filter_by(id=pid).first()
            if p_record:
                product_name = p_record.data.get("Nombre") or p_record.data.get("COD") or product_name
                
            # Agrupar ventas diarias de este producto
            daily_prod_sales = {d: 0.0 for d in days}
            for s in recent_sales:
                if s.timestamp:
                    s_local_date = (s.timestamp - tz_offset).date()
                    if s_local_date in daily_prod_sales:
                        qty_sold = 0.0
                        items = s.details.get("items", [])
                        for item in items:
                            if item.get("record_id") == pid:
                                qty_sold += float(item.get("quantity_change", 0.0))
                        daily_prod_sales[s_local_date] += qty_sold
                        
            product_data = [round(daily_prod_sales[d], 2) for d in days]
            color = colors[idx % len(colors)]
            chart_datasets.append({
                "label": f"{product_name} (Cant)",
                "data": product_data,
                "borderColor": color,
                "backgroundColor": "transparent",
                "tension": 0.4,
                "fill": False
            })
    else:
        # Agrupar ventas totales diarias
        daily_sales = {d: 0.0 for d in days}
        for s in recent_sales:
            if s.timestamp:
                s_local_date = (s.timestamp - tz_offset).date()
                if s_local_date in daily_sales:
                    daily_sales[s_local_date] += float(s.details.get("total", 0.0))
                    
        chart_data = [round(daily_sales[d], 2) for d in days]
        
        chart_datasets.append({
            "label": "Ventas Totales ($)",
            "data": chart_data,
            "borderColor": "#10b981",
            "backgroundColor": "rgba(16, 185, 129, 0.1)",
            "tension": 0.4,
            "fill": True
        })
        
    # Calcular productos más y menos vendidos
    products_map = {}
    if inv_table:
        for r in inv_table.records:
            name = r.data.get("Nombre") or r.data.get("COD") or f"Producto #{r.id}"
            sku = r.data.get("COD") or ""
            price_val = r.data.get("Precio por Unidad") or r.data.get("Precio") or r.data.get("P. Venta") or 0.0
            try:
                price = float(price_val)
            except (ValueError, TypeError):
                price = 0.0
            
            stock_val = r.data.get("Cantidad") or r.data.get("Stock") or 0
            try:
                stock = int(float(stock_val))
            except (ValueError, TypeError):
                stock = 0

            products_map[r.id] = {
                "id": r.id,
                "name": name,
                "sku": sku,
                "price": price,
                "stock": stock,
                "sold_qty": 0.0,
                "revenue": 0.0
            }

    for s in recent_sales:
        items = s.details.get("items", []) if s.details else []
        for item in items:
            pid = item.get("record_id")
            if pid is None:
                continue
            try:
                qty = float(item.get("quantity_change", 0.0))
            except (ValueError, TypeError):
                qty = 0.0
            try:
                subtotal = float(item.get("subtotal", 0.0))
            except (ValueError, TypeError):
                subtotal = 0.0
                
            if pid in products_map:
                products_map[pid]["sold_qty"] += qty
                products_map[pid]["revenue"] += subtotal
            else:
                products_map[pid] = {
                    "id": pid,
                    "name": item.get("name") or f"Producto #{pid}",
                    "sku": "",
                    "price": float(item.get("price", 0.0)) if item.get("price") is not None else 0.0,
                    "stock": 0,
                    "sold_qty": qty,
                    "revenue": subtotal
                }

    all_prods = list(products_map.values())
    top_sold_sorted = sorted(all_prods, key=lambda x: x["sold_qty"], reverse=True)
    top_sold = top_sold_sorted[:3]

    remaining_prods = [p for p in all_prods if p not in top_sold]
    if len(remaining_prods) >= 3:
        least_sold_sorted = sorted(remaining_prods, key=lambda x: x["sold_qty"])
    else:
        least_sold_sorted = sorted(all_prods, key=lambda x: x["sold_qty"])
    
    least_sold = least_sold_sorted[:3]

    for p in top_sold:
        p["revenue"] = round(p["revenue"], 2)
    for p in least_sold:
        p["revenue"] = round(p["revenue"], 2)

    return {
        "stats": {
            "total_sales": round(total_sales, 2),
            "total_purchases": round(total_purchases, 2),
            "gain_net": round(gain_net, 2),
            "total_transactions": total_transactions,
            "low_stock_count": low_stock_count
        },
        "chart": {
            "labels": chart_labels,
            "datasets": chart_datasets
        },
        "top_sold": top_sold,
        "least_sold": least_sold
    }

@app.get("/api/dashboard/products", tags=["admin"])
def api_get_dashboard_products(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
        
    inv_table = db.query(models.AppTable).filter(models.AppTable.business_id == user.business_id, models.AppTable.name.ilike('inventario%')).first()
    if not inv_table:
        return []
        
    results = []
    for r in inv_table.records:
        name = r.data.get("Nombre") or "Sin nombre"
        sku = r.data.get("COD") or ""
        results.append({
            "id": r.id,
            "name": name,
            "sku": sku
        })
    return results
