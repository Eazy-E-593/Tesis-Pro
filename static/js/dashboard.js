const templatesConfig = {
    'restaurant': {
        title: 'Restaurante / Comida',
        tables: [
            { icon: 'users', name: 'Clientes', desc: 'Directorio de clientes frecuentes.', cols: ['Nombre', 'Teléfono', 'Correo', 'Frecuencia'] },
            { icon: 'truck', name: 'Proveedores', desc: 'Suministradores de insumos.', cols: ['Empresa', 'Contacto', 'Producto', 'Pago'] },
            { icon: 'package', name: 'Inventario', desc: 'Materia prima e ingredientes.', cols: ['Producto', 'Stock', 'Mínimo', 'Unidad'] },
            { icon: 'scroll-text', name: 'Menú', desc: 'Catálogo de platillos y precios.', cols: ['Nombre', 'Descripción', 'Precio', 'Categoría'] },
            { icon: 'receipt', name: 'Pedidos (Ventas)', desc: 'Registro de consumos.', cols: ['Mesa', 'Cliente', 'Items', 'Total', 'Estado'] }
        ]
    },
    'store': {
        title: 'Tienda / Minimarket',
        tables: [
            { icon: 'users', name: 'Clientes', desc: 'Compradores registrados y fidelización.', cols: ['Nombre', 'WhatsApp', 'Puntos', 'Última Compra'] },
            { icon: 'truck', name: 'Proveedores', desc: 'Distribuidores de mercancía.', cols: ['Nombre', 'RUC', 'Teléfono', 'Crédito'] },
            { icon: 'package', name: 'Inventario', desc: 'Catálogo de productos para venta.', cols: ['Producto', 'Código', 'Stock', 'P. Venta'] },
            { icon: 'shopping-cart', name: 'Ventas', desc: 'Registro de transacciones diarias.', cols: ['Cajero', 'Cliente', 'Met. Pago', 'Total'] }
        ]
    },
    'gym': {
        title: 'Gimnasio / Centro Fitness',
        tables: [
            { icon: 'users', name: 'Socios (Clientes)', desc: 'Miembros activos del gimnasio.', cols: ['Socio', 'DNI', 'Teléfono', 'Edad'] },
            { icon: 'truck', name: 'Proveedores', desc: 'Suministros y mantenimiento.', cols: ['Empresa', 'Servicio', 'Contacto'] },
            { icon: 'credit-card', name: 'Planes', desc: 'Membresías (Mensual, Anual, etc).', cols: ['Plan', 'Costo', 'Días', 'Acceso'] },
            { icon: 'clipboard-check', name: 'Suscripciones (Ventas)', desc: 'Registro de pagos de planes.', cols: ['Socio', 'Plan', 'Inicio', 'Vence', 'Monto'] }
        ]
    },
    'liquor': {
        title: 'Licorería / Bar',
        tables: [
            { icon: 'users', name: 'Clientes', desc: 'Compradores frecuentes.', cols: ['Nombre', 'Edad', 'WhatsApp'] },
            { icon: 'truck', name: 'Proveedores', desc: 'Distribuidores de licores.', cols: ['Marca', 'Proveedor', 'Pedido Mín.'] },
            { icon: 'package', name: 'Inventario', desc: 'Catálogo de bebidas y stock.', cols: ['Marca', 'Tipo', 'Grado', 'Stock', 'P. Venta'] },
            { icon: 'glass-water', name: 'Ventas', desc: 'Transacciones y despachos.', cols: ['Vendedor', 'Items', 'Subtotal', 'Total'] }
        ]
    }
};

function showTemplateModal(type) {
    const config = templatesConfig[type];
    if (!config) return;

    document.getElementById('template-modal-title').textContent = `¿Tu negocio es un ${config.title}?`;

    const listContainer = document.getElementById('template-tables-list');
    listContainer.innerHTML = ''; // Clear previous

    config.tables.forEach(table => {
        const item = document.createElement('div');
        item.className = 'suggestion-item'; // Use the class for styling
        item.style.display = 'flex';
        item.style.alignItems = 'flex-start';
        item.style.gap = '12px';
        item.style.background = 'var(--bg-main)';
        item.style.padding = '16px';
        item.style.borderRadius = '12px';
        item.style.border = '1px solid var(--border-glass)';

        // Preview columns tooltip
        const preview = document.createElement('div');
        preview.className = 'columns-preview';
        preview.innerHTML = `<div style="font-weight: 600; font-size: 0.8rem; margin-bottom: 8px; color: #fff;">Columnas sugeridas:</div>
                             <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                                ${table.cols.map(c => `<span class="column-tag">${c}</span>`).join('')}
                             </div>`;

        // Icon
        const iconDiv = document.createElement('div');
        iconDiv.style.color = 'var(--primary)';
        iconDiv.innerHTML = `<i data-lucide="${table.icon}" style="width: 24px; height: 24px;"></i>`;

        // Text
        const textDiv = document.createElement('div');
        textDiv.innerHTML = `<strong style="display: block; color: var(--text-main); font-size: 1rem; margin-bottom: 4px;">${table.name}</strong>
                             <span style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4; display: block;">${table.desc}</span>`;

        item.appendChild(preview); // Add tooltip
        item.appendChild(iconDiv);
        item.appendChild(textDiv);
        listContainer.appendChild(item);
    });

    // Re-initialize lucide icons for the newly added HTML
    lucide.createIcons();

    // Show panel and scroll to it smoothly
    const panel = document.getElementById('template-suggestion-panel');
    panel.style.display = 'block';
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function confirmTemplateCreation() {
    // Mostrar notificación temporal nativa
    showToast('Esta funcionalidad se implementará pronto. Por ahora el diseño visual está listo.', 'info');
    document.getElementById('template-suggestion-panel').style.display = 'none';
}
