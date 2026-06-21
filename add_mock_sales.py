import datetime
import random
from database import SessionLocal
from models import Business, User, AppTable, AppRecord, AppAudit

def create_mock_sales():
    db = SessionLocal()
    try:
        # Obtener el primer negocio registrado
        business = db.query(Business).first()
        if not business:
            print("No se encontró ningún negocio en la base de datos. Por favor regístrate primero.")
            return

        print(f"Negocio seleccionado: {business.name} (ID: {business.id})")

        # Obtener el primer administrador o usuario del negocio
        user = db.query(User).filter(User.business_id == business.id).first()
        employee_code = user.employee_code if user else "EMP-SYSTEM"

        # Buscar la tabla de inventario para este negocio
        inv_table = db.query(AppTable).filter(
            AppTable.business_id == business.id, 
            AppTable.name.ilike('inventario%')
        ).first()

        products = []
        if inv_table:
            products = db.query(AppRecord).filter(AppRecord.table_id == inv_table.id).all()
        
        if not products:
            print("Advertencia: No se encontraron productos en la tabla de Inventario.")
            print("Se crearán ventas sin productos específicos (ventas globales).")

        # Generar ventas para los últimos 10 días
        tz_offset = datetime.timedelta(hours=5)  # UTC-5 Ecuador
        now_local = datetime.datetime.utcnow() - tz_offset
        
        print("\nGenerando facturas de prueba para los últimos 10 días...")
        
        sales_created = 0
        for days_back in range(10, -1, -1):
            # Fecha local de la venta ficticia
            target_local_date = now_local - datetime.timedelta(days=days_back)
            
            # Generar entre 1 y 4 ventas por día
            num_sales = random.randint(1, 4)
            for _ in range(num_sales):
                # Generar hora aleatoria en el día
                hour = random.randint(8, 20)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                sale_datetime_local = target_local_date.replace(
                    hour=hour, minute=minute, second=second, microsecond=0
                )
                # Convertir a UTC para guardarlo en la base de datos
                sale_datetime_utc = sale_datetime_local + tz_offset
                
                # Armar los productos de esta venta
                items = []
                total = 0.0
                
                if products:
                    # Elegir 1 o 2 productos aleatorios
                    chosen_products = random.sample(products, min(len(products), random.randint(1, 2)))
                    for prod in chosen_products:
                        qty = random.randint(1, 5)
                        # Obtener precio
                        price_val = prod.data.get("Precio por Unidad") or prod.data.get("Precio") or prod.data.get("P. Venta") or 10.0
                        try:
                            price = float(price_val)
                        except (ValueError, TypeError):
                            price = 10.0
                        
                        subtotal = qty * price
                        total += subtotal
                        items.append({
                            "record_id": prod.id,
                            "quantity_change": float(qty),
                            "name": prod.data.get("Nombre") or prod.data.get("COD") or f"Producto #{prod.id}",
                            "price": price,
                            "subtotal": subtotal
                        })
                else:
                    # Venta aleatoria sin productos
                    total = round(random.uniform(15.0, 150.0), 2)
                
                subtotal_calc = total / 1.15
                iva_calc = total - subtotal_calc
                
                details = {
                    "type": "Venta",
                    "client_name": random.choice(["Consumidor Final", "Juan Pérez", "María Rodríguez", "Carlos Gómez"]),
                    "client_cedula": random.choice(["9999999999", "1723456789", "0912345678", None]),
                    "subtotal": round(subtotal_calc, 2),
                    "iva": round(iva_calc, 2),
                    "total": round(total, 2),
                    "items": items
                }
                
                client_label = details["client_name"]
                cedula_text = f" | Cédula/RUC: {details['client_cedula']}" if details['client_cedula'] else ""
                action_text = f"Venta | Cliente: {client_label}{cedula_text} | Total: ${total:.2f}"
                
                audit = AppAudit(
                    business_id=business.id,
                    table_id=inv_table.id if inv_table else None,
                    record_id=None,
                    employee_code=employee_code,
                    action=action_text,
                    details=details,
                    timestamp=sale_datetime_utc,
                    status="active"
                )
                db.add(audit)
                sales_created += 1
                
        db.commit()
        print(f"¡Éxito! Se han creado {sales_created} facturas de prueba distribuidas en los últimos 10 días.")
        print("El gráfico del dashboard debería actualizarse automáticamente.")
        
    except Exception as e:
        db.rollback()
        print(f"Error al generar facturas de prueba: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_mock_sales()
