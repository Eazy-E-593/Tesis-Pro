# MicroBase - Herramienta No-Code para PYMES 📦🚀

**Diseño y Prototipado de una herramienta no-code para la digitalización de la gestión de inventario y ventas en Pymes.**

MicroBase es una plataforma SaaS (Software as a Service) modular y dinámica, diseñada específicamente para dueños de microempresas y pymes. Su objetivo principal es cerrar la brecha digital al permitir a "desarrolladores ciudadanos" (usuarios sin experiencia técnica) crear y gestionar bases de datos estructuradas de manera intuitiva, rápida y económica.

---

## 🌟 Características Principales

*   **Creador de Recursos Dinámicos (No-Code):** Permite a los administradores crear sus propias tablas y columnas personalizadas (ej. Inventario, Clientes, Proveedores, Horarios) sin escribir código, estructurando datos operativos en minutos.
*   **Módulo POS (Point of Sale) Inteligente**: 
    *   **Identificación y Búsqueda Avanzada**: Búsqueda flexible de clientes por Nombre o por Cédula/RUC.
    *   **Auto-llenado Cruzado**: Autocompleta automáticamente la cédula cuando se selecciona un nombre y viceversa.
    *   **Enforzamiento Físico de Dígitos**: Control estricto a nivel de teclado que restringe la entrada a exactamente 10 dígitos (Cédula) o 13 dígitos (RUC).
    *   **Consumidor Final Fast-Checkout**: Checkbox integrado que bloquea y autocompleta instantáneamente la venta con "Consumidor Final" y el RUC genérico `9999999999`.
*   **Facturación y Tickets Térmicos**: Generación automática de tickets en formato de rollo térmico (58mm) al procesar movimientos y facturas, con opciones de exportación de información en formatos comunes como CSV y PDF.
*   **Seguridad y Acceso Basado en Roles (RBAC)**: Blindaje de seguridad estricto con jerarquías estándar mediante bloqueo de Backend y Frontend:
    *   **Admin/Dueño:** Acceso absoluto a todas las tablas, nómina, finanzas y configuración.
    *   **Gerente:** Control operativo del negocio y gestión de compras y ventas.
    *   **Bodeguero:** Control logístico enfocado en ingresos de stock (Compras).
    *   **Cajero:** Control focalizado en salida de mercancía e ingresos de caja (Ventas). Oculta la información de personal para evitar fraudes.
*   **Auditoría Extendida**: 
    *   Historial Fiscal centralizado con registro imborrable del detalle de cada transacción (Operador, total facturado y cliente).
    *   Cierre de filas (`readOnly`) después de salvadas para prevenir sobreescritura accidental.

## 🛠️ Stack Tecnológico

El desarrollo de esta propuesta tecnológica se basa en el siguiente ecosistema:

*   **Backend:** Python con [FastAPI](https://fastapi.tiangolo.com/) garantizando un rendimiento ágil y escalable.
*   **Base de Datos:** PostgreSQL (Nativo) con SQLAlchemy y diseño de ORM para el manejo estructurado de datos.
*   **Renderizado de Vistas:** Jinja2.
*   **Frontend:** HTML5, CSS3 Vanilla y JavaScript Vanilla, aplicando principios rigurosos de usabilidad y diseño (Glassmorphism) para facilitar la adopción por parte del usuario final.

## ⚙️ Instalación y Configuración

### 1. Preparar Entorno
```bash
python -m venv venv
# Activar (Windows): venv\Scripts\activate
# Activar (Linux/Mac): source venv/bin/activate
pip install -r requirements.txt
```

### 2. Base de Datos
Crea una base de datos en PostgreSQL y configura tu URL en un archivo `.env` en la raíz del proyecto:
```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/microbase
```

### 3. Ejecución
Inicia el servidor local para entorno de desarrollo:
```bash
uvicorn main:app --reload
```
Navega a `http://127.0.0.1:8000/` para comenzar.

## 🗺️ Roadmap (Próximas Fases del Prototipo)
- **Dashboard Analítico:** Implementación de gráficas para el rendimiento financiero y toma de decisiones basada en evidencia.
- **Multitenancy:** Soporte avanzado para multi-sucursales.
- **Gestión Avanzada:** Integración con más herramientas de análisis en tiempo real orientadas al ecosistema Low-Code y No-Code.

---
*Desarrollado como Proyecto de Titulación - Ingeniería en Sistemas de la Información*
**Autores:** Castillo Mina Williams Johao & Molina Balseca Geanella Valentina (2025)
