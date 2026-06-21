import json
import sys
import os
from sqlalchemy.orm import Session

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database
import models

def restore_to_business(business_code: str):
    db = next(database.get_db())
    
    # 1. Find the target business
    business = db.query(models.Business).filter(models.Business.code == business_code).first()
    if not business:
        print(f"Error: No se encontró ningún negocio con el código: '{business_code}'")
        return False
        
    print(f"Negocio encontrado: {business.name} (ID: {business.id})")
    
    # 2. Load backup data
    backup_file = "backup_data.json"
    if not os.path.exists(backup_file):
        print(f"Error: El archivo de respaldo {backup_file} no existe.")
        return False
        
    with open(backup_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("Cargando datos del archivo de respaldo...")
    
    # 3. Clean existing tables for this business to avoid conflicts
    print("Limpiando tablas iniciales del negocio...")
    existing_tables = db.query(models.AppTable).filter(models.AppTable.business_id == business.id).all()
    for t in existing_tables:
        db.query(models.AppField).filter(models.AppField.table_id == t.id).delete()
        db.query(models.AppRecord).filter(models.AppRecord.table_id == t.id).delete()
        db.delete(t)
    db.commit()
    
    # 4. Restore tables and fields
    old_to_new_table_ids = {}
    
    print("\nRestaurando tablas...")
    for t_data in data.get("tables", []):
        new_table = models.AppTable(
            name=t_data["name"],
            description=t_data.get("description"),
            business_id=business.id
        )
        db.add(new_table)
        db.commit()
        db.refresh(new_table)
        old_to_new_table_ids[t_data["id"]] = new_table.id
        print(f" - Tabla '{new_table.name}' recreada (Nueva ID: {new_table.id})")
        
    print("\nRestaurando columnas (campos)...")
    for f_data in data.get("fields", []):
        old_table_id = f_data["table_id"]
        if old_table_id not in old_to_new_table_ids:
            continue
        new_table_id = old_to_new_table_ids[old_table_id]
        
        new_field = models.AppField(
            table_id=new_table_id,
            name=f_data["name"],
            field_type=f_data["field_type"],
            options=f_data.get("options"),
            order_index=f_data.get("order_index")
        )
        db.add(new_field)
    db.commit()
    print("Columnas restauradas.")
    
    # 5. Restore records
    print("\nRestaurando registros de datos...")
    records_count = 0
    for r_data in data.get("records", []):
        old_table_id = r_data["table_id"]
        if old_table_id not in old_to_new_table_ids:
            continue
        new_table_id = old_to_new_table_ids[old_table_id]
        
        new_record = models.AppRecord(
            table_id=new_table_id,
            data=r_data["data"]
        )
        db.add(new_record)
        records_count += 1
    db.commit()
    print(f"Se restauraron {records_count} registros con éxito.")
    
    # 6. Restore Users (linking them to this business, preserving roles/emails if possible)
    # We update status to active and update business_id for users with matching emails
    print("\nRestaurando / actualizando usuarios...")
    for u_data in data.get("users", []):
        existing_user = db.query(models.User).filter(models.User.email == u_data["email"]).first()
        if existing_user:
            existing_user.business_id = business.id
            existing_user.role = u_data["role"]
            existing_user.status = "active"
            print(f" - Usuario existente actualizado: {existing_user.email} (Rol: {existing_user.role})")
        else:
            # Create user with a temporary password (same as email for safety or simple pass)
            new_user = models.User(
                email=u_data["email"],
                full_name=u_data["full_name"],
                hashed_password="password123", # default
                role=u_data["role"],
                employee_code=f"EMP-{u_data['id']}",
                cedula=u_data.get("cedula"),
                business_id=business.id,
                status="active"
            )
            db.add(new_user)
            print(f" - Nuevo usuario creado desde respaldo: {new_user.email} (Contraseña temporal: password123)")
    db.commit()
    print("\n¡Proceso de restauración completado con éxito!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python restore_backup.py <CODIGO_DEL_NEGOCIO>")
        sys.exit(1)
        
    code = sys.argv[1].upper().strip()
    restore_to_business(code)
