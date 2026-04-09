import sqlite3
conn = sqlite3.connect('microbase.db')
c = conn.cursor()
c.execute("UPDATE app_fields SET name = 'Unidad de Venta' WHERE name = 'Unidad'")
conn.commit()
conn.close()
print("Migración completada")
