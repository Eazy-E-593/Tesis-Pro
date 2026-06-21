import sys
import os

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database
import models

def delete_business(business_code: str):
    db = next(database.get_db())
    
    # Find business
    business = db.query(models.Business).filter(models.Business.code == business_code).first()
    if not business:
        print(f"Error: No se encontró ningún negocio con el código: '{business_code}'")
        return False
        
    print(f"Negocio encontrado: '{business.name}' con código '{business.code}'")
    confirm = input("¿Estás seguro de que deseas eliminar este negocio y TODOS sus usuarios, tablas y registros asociados? (si/no): ")
    if confirm.lower().strip() != "si":
        print("Operación cancelada.")
        return False
        
    print("Eliminando negocio y todos sus datos en cascada...")
    db.delete(business)
    db.commit()
    print("¡Negocio eliminado exitosamente!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python delete_business.py <CODIGO_DEL_NEGOCIO>")
        sys.exit(1)
        
    code = sys.argv[1].upper().strip()
    delete_business(code)
