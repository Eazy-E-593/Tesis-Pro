from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE app_fields ADD COLUMN order_index INTEGER;"))
        # Set initial order based on field id (preserves current DB order)
        conn.execute(text("UPDATE app_fields SET order_index = id WHERE order_index IS NULL;"))
        conn.commit()
        print("order_index column added and initialized!")
    except Exception as e:
        print("Error:", e)
