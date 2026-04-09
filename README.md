# MicroBase ERP y Sistema POS 📦🚀

MicroBase es una plataforma SaaS (Software as a Service) modular y dinámica, diseñada específicamente para dueños de microempresas y pymes. Permite gestionar inventarios, nóminas, bases de clientes y realizar operaciones de venta/compra en un entorno seguro, escalable y con una interfaz "No-Code" extremadamente amigable.

## 🌟 Características Principales

*   **Creador de Recursos Dinámicos (No-Code):** Permite a los administradores crear sus propias tablas y columnas personalizadas (ej. Inventario, Clientes, Horarios) sin escribir una sola línea de código.
*   **Módulo POS (Point of Sale):** Panel inteligente que detecta si estás en "Inventario" para habilitar herramientas fiscales de facturación de Salidas (Ventas) e Ingresos (Compras).
*   **Acceso Basado en Roles (RBAC):** Blindaje de seguridad estricto con jerarquías estándar de la industria mediante bloqueo de Backend y Frontend:
    *   **Admin/Dueño:** Acceso absoluto a todas las tablas, nómina, finanzas y configuración.
    *   **Gerente:** Control operativo del negocio y gestión de compras y ventas.
    *   **Bodeguero:** Control logístico enfocado únicamente a inyectar ingresos de stock.
    *   **Cajero:** Control focalizado en salida de mercancía e ingresos de caja. Ocultando la visualización de personal/nómina para evitar fraude ético.
*   **Integridad de Datos Automática:** 
    *   Generación de `SKU/COD` autogenerado para productos.
    *   Cierre en bloque (`readOnly`) de filas después de salvadas para prevenir la sobreescritura accidental o errores de dedo.
*   **Cámara de Auditoría Global:** Historial Fiscal centralizado con registro imborrable de todos los movimientos de capital de trabajo y logs de seguridad según el empleado que ejecutó la acción.
*   **Diseño de Vanguardia (UI/UX):** Glassmorphism en tarjetas informativas, soporte total para **Modo Oscuro/Modo Claro**, y adaptación de **Zoom Global (Accesibilidad Visual)** que guarda la preferencia del operario localmente.

## 🛠️ Stack Tecnológico

*   **Backend:** Python con [FastAPI](https://fastapi.tiangolo.com/).
*   **Base de Datos:** SQLite automatizada con [SQLAlchemy] y diseño de ORM.
*   **Renderizado de Vistas:** Jinja2 (Inyectando HTML servido en tiempo real desde el Backend).
*   **Frontend (Lógica Lado Cliente):** HTML5 Semántico, CSS3 Vanilla (`style.css`), y JavaScript Vanilla (`app.js`).
*   **Íconos Visuales:** Sistema Lucide.

## ⚙️ Instalación y Configuración (Entorno de Desarrollo)

### 1. Clonar y preparar entorno
Abre tu consola en tu entorno de trabajo favorito y clona los componentes. Es totalmente recomendable usar un entorno virtual (`venv`):

```bash
python -m venv venv
```
Activar el entorno:
*   En **Windows**: `venv\Scripts\activate`
*   En **Linux/Mac**: `source venv/bin/activate`

### 2. Instalar Módulos
Habiendo activado tu entorno virtual:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar Sistema Central Base de Datos
Microbase usa un servidor ASGI (Uvicorn). Lánzalo desde el terminal utilizando este comando, activando `reload` para reconstruir la caché al editar código en caliente:
```bash
uvicorn main:app --reload
```

Posteriormente, navega a `http://127.0.0.1:8000/dashboard` en tu navegador. 

## 🗺️ Futuros Desarrollos (Roadmap v2.0)
- Generación de Tickets y Facturas Digitales en formato PDF exportables e imprimibles bajo estándares comerciales.
- Multitenancy: Creación de instancias modulares para albergar una rama corporativa multi-sucursal y diseñador de Roles Customizados sin tocar el código fuente.
- Migración de SQLite a infraestructura PostgreSQL de producción.
