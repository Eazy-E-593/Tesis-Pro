import json
from database import SessionLocal
from models import User, AppTable, AppField, AppRecord, AppAudit

def backup_db():
    db = SessionLocal()
    try:
        users = [{"id": u.id, "full_name": u.full_name, "email": u.email, "role": u.role, "cedula": u.cedula} for u in db.query(User).all()]
        tables = [{"id": t.id, "name": t.name, "description": t.description} for t in db.query(AppTable).all()]
        fields = [{"id": f.id, "table_id": f.table_id, "name": f.name, "field_type": f.field_type, "options": f.options, "order_index": f.order_index} for f in db.query(AppField).all()]
        records = [{"id": r.id, "table_id": r.table_id, "data": r.data} for r in db.query(AppRecord).all()]
        
        backup_data = {
            "users": users,
            "tables": tables,
            "fields": fields,
            "records": records
        }
        
        with open("backup_data.json", "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=4)
        print("Backup completed successfully to backup_data.json")
    finally:
        db.close()

if __name__ == "__main__":
    backup_db()
