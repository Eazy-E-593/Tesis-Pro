# MicroBase ERP y Sistema POS 📦🚀

MicroBase es una plataforma SaaS (Software as a Service) modular y dinámica, diseñada específicamente para dueños de microempresas y pymes. Permite gestionar inventarios, nóminas, bases de clientes y realizar operaciones de venta/compra en un entorno seguro, escalable y con una interfaz "No-Code" extremadamente amigable.

## 🌟 Características Principales

*   **Creador de Recursos Dinámicos (No-Code):** Permite a los administradores crear sus propias tablas y columnas personalizadas (ej. Inventario, Clientes, Proveedores, Horarios) sin escribir una sola línea de código.
*   **Módulo POS (Point of Sale) Inteligente:** Panel que detecta el tipo de operación. Separa automáticamente el flujo de **Ventas (Clientes)** y **Compras (Proveedores)**, gestionando el stock de forma integral.
*   **Facturación y Tickets Térmicos:** Generación automática de tickets en formato de rollo térmico (58mm) al procesar movimientos, con posibilidad de re-impresión desde el historial.
*   **Acceso Basado en Roles (RBAC):** Blindaje de seguridad estricto con jerarquías estándar de la industria mediante bloqueo de Backend y Frontend:
    *   **Admin/Dueño:** Acceso absoluto a todas las tablas, nómina, finanzas y configuración.
    *   **Gerente:** Control operativo del negocio y gestión de compras y ventas.
    *   **Bodeguero:** Control logístico enfocado únicamente a inyectar ingresos de stock (Compras).
    *   **Cajero:** Control focalizado en salida de mercancía e ingresos de caja (Ventas). Ocultando la visualización de personal/nómina para evitar fraude ético.
*   **Integridad de Datos y Auditoría:** 
    *   Generación de `SKU/COD` autogenerado para productos.
    *   **Cámara de Auditoría Global:** Historial Fiscal centralizado con registro imborrable del detalle de cada transacción, garantizando la inmutabilidad de precios y cantidades en el tiempo.
    *   Cierre en bloque (`readOnly`) de filas después de salvadas para prevenir la sobreescritura accidental.

## 🛠️ Stack Tecnológico

*   **Backend:** Python con [FastAPI](https://fastapi.tiangolo.com/).
*   **Base de Datos:** PostgreSQL (Nativo) con [SQLAlchemy] y diseño de ORM.
*   **Renderizado de Vistas:** Jinja2.
*   **Frontend:** HTML5, CSS3 Vanilla y JavaScript Vanilla (Diseño Glassmorphism).

## ⚙️ Instalación y Configuración

### 1. Preparar Entorno
```bash
python -m venv venv
# Activar (Windows): venv\Scripts\activate
# Activar (Linux/Mac): source venv/bin/activate
pip install -r requirements.txt
```

### 2. Base de Datos
Crea una base de datos en PostgreSQL y configura tu URL en un archivo `.env`:
```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/microbase
```

### 3. Ejecutar
```bash
uvicorn main:app --reload
```
Navega a `http://127.0.0.1:8000/` para comenzar.

## 🗺️ Futuros Desarrollos (Roadmap v2.0)
- Dashboard Analítico con gráficas de rendimiento financiero.
- Exportación masiva de tablas a formatos Excel/CSV.
- Multitenancy: Soporte para multi-sucursales.

