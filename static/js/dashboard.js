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

let selectedTemplateType = null;

function showTemplateModal(type) {
    selectedTemplateType = type;
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

function confirmTemplate() {
    if (!selectedTemplateType) {
        showToast('Por favor selecciona una plantilla', 'error');
        return;
    }
    
    const btn = document.getElementById('btn-confirm-template');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Creando tablas...';
    }
    
    fetch('/api/business/setup-template', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ template: selectedTemplateType })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error('Error al configurar la plantilla');
        }
        return res.json();
    })
    .then(data => {
        showToast('Plantilla configurada correctamente', 'success');
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    })
    .catch(err => {
        console.error(err);
        showToast(err.message || 'Error al configurar la plantilla', 'error');
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Sí, crear estas tablas';
        }
    });
}

function confirmTemplateCreation() {
    confirmTemplate();
}

// Lógica del Dashboard Analítico e Interactivo
let productsCache = [];
let selectedProducts = [];
let salesChartInstance = null;
let pollingIntervalId = null;

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

function initAdminDashboard() {
    loadProductsCache();
    updateDashboardData();
    
    // Configurar polling cada 5 segundos
    pollingIntervalId = setInterval(updateDashboardData, 5000);
    
    // Ocultar dropdown de autocompletado si se hace click fuera
    document.addEventListener('click', (e) => {
        const searchInput = document.getElementById('dash-prod-search');
        const resultsDiv = document.getElementById('dash-prod-results');
        if (searchInput && resultsDiv) {
            if (!searchInput.contains(e.target) && !resultsDiv.contains(e.target)) {
                resultsDiv.style.display = 'none';
            }
        }
    });
}

function loadProductsCache() {
    fetch('/api/dashboard/products')
    .then(res => {
        if (!res.ok) throw new Error('No se pudo cargar la lista de productos');
        return res.json();
    })
    .then(data => {
        productsCache = data;
    })
    .catch(err => console.error('Error cargando cache de productos:', err));
}

function updateDashboardData() {
    const productIds = selectedProducts.map(p => p.id).join(',');
    const startDate = document.getElementById('dash-start-date')?.value || '';
    const endDate = document.getElementById('dash-end-date')?.value || '';
    
    let params = [];
    if (productIds) params.push(`products=${productIds}`);
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    
    const queryString = params.length > 0 ? `?${params.join('&')}` : '';
    const url = `/api/dashboard/stats${queryString}`;
    
    fetch(url)
    .then(res => {
        if (!res.ok) throw new Error('Error al obtener estadísticas del dashboard');
        return res.json();
    })
    .then(data => {
        // Actualizar tarjetas de KPI
        const totalSalesEl = document.getElementById('dash-total-sales');
        const totalPurchasesEl = document.getElementById('dash-total-purchases');
        const netProfitEl = document.getElementById('dash-net-profit');
        const totalTxEl = document.getElementById('dash-total-tx');
        
        if (totalSalesEl) totalSalesEl.textContent = formatCurrency(data.stats.total_sales);
        if (totalPurchasesEl) totalPurchasesEl.textContent = formatCurrency(data.stats.total_purchases);
        
        if (netProfitEl) {
            netProfitEl.textContent = formatCurrency(data.stats.gain_net);
            if (data.stats.gain_net < 0) {
                netProfitEl.style.color = 'var(--danger)';
            } else {
                netProfitEl.style.color = 'var(--primary)';
            }
        }
        
        if (totalTxEl) totalTxEl.textContent = data.stats.total_transactions;
        
        // Alerta de stock bajo
        const lowStockAlert = document.getElementById('dash-low-stock-alert');
        const lowStockCount = document.getElementById('dash-low-stock-count');
        if (lowStockAlert && lowStockCount) {
            if (data.stats.low_stock_count > 0) {
                lowStockCount.textContent = data.stats.low_stock_count;
                lowStockAlert.style.display = 'flex';
            } else {
                lowStockAlert.style.display = 'none';
            }
        }
        
        // Actualizar gráfico de Chart.js
        renderSalesChart(data.chart.labels, data.chart.datasets);

        // Actualizar productos más y menos vendidos
        renderProductPerformanceList('top-sold-list', data.top_sold, 'top');
        renderProductPerformanceList('least-sold-list', data.least_sold, 'least');
    })
    .catch(err => console.error('Error en polling de dashboard:', err));
}

function renderProductPerformanceList(containerId, products, type) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!products || products.length === 0) {
        container.innerHTML = `
            <div style="padding: 24px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">
                <i data-lucide="package" style="width: 24px; height: 24px; margin: 0 auto 8px; display: block; opacity: 0.5;"></i>
                No hay datos disponibles
            </div>
        `;
        lucide.createIcons();
        return;
    }

    container.innerHTML = '';
    products.forEach((prod, index) => {
        const rankNum = index + 1;
        const rankClass = `rank-${type}-${rankNum}`;
        
        // Formatear cantidades para omitir decimales si es entero
        const qtyStr = Number.isInteger(prod.sold_qty) 
            ? prod.sold_qty 
            : prod.sold_qty.toFixed(2).replace(/\.00$/, '');

        const item = document.createElement('div');
        item.className = 'product-performance-item';
        
        item.innerHTML = `
            <div class="product-info-wrapper">
                <div class="product-rank ${rankClass}">
                    ${rankNum}°
                </div>
                <div class="product-details">
                    <span class="product-name" title="${prod.name}">${prod.name}</span>
                    <span class="product-sku">${prod.sku ? 'SKU: ' + prod.sku : 'Sin SKU'}</span>
                </div>
            </div>
            <div class="product-stats">
                <span class="product-qty">${qtyStr} u.</span>
                <span class="product-revenue">${formatCurrency(prod.revenue)}</span>
            </div>
        `;
        container.appendChild(item);
    });
    
    lucide.createIcons();
}

function onDateFilterChange() {
    updateDashboardData();
}

function clearDateFilter() {
    const startDateEl = document.getElementById('dash-start-date');
    const endDateEl = document.getElementById('dash-end-date');
    if (startDateEl) startDateEl.value = '';
    if (endDateEl) endDateEl.value = '';
    updateDashboardData();
}

function renderSalesChart(labels, datasets) {
    const canvas = document.getElementById('salesChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Modificar estilos de los datasets para que tengan una estética premium
    const styledDatasets = datasets.map(ds => {
        if (ds.fill && ds.borderColor === '#10b981') {
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(16, 185, 129, 0.3)');
            gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');
            ds.backgroundColor = gradient;
        }
        
        ds.borderWidth = 3;
        ds.pointBackgroundColor = ds.borderColor;
        ds.pointBorderColor = '#171821'; // Oscuro premium a tono con el fondo
        ds.pointBorderWidth = 2;
        ds.pointRadius = 4;
        ds.pointHoverRadius = 6;
        ds.pointHoverBorderWidth = 3;
        
        return ds;
    });
    
    if (salesChartInstance) {
        salesChartInstance.data.labels = labels;
        salesChartInstance.data.datasets = styledDatasets;
        salesChartInstance.update('none'); // Update sin animaciones repetidas para que sea fluido
    } else {
        salesChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: styledDatasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#94a3b8',
                            font: {
                                family: 'Inter',
                                size: 12,
                                weight: '500'
                            },
                            boxWidth: 12,
                            usePointStyle: true,
                            pointStyle: 'circle'
                          }
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#f8fafc',
                        bodyColor: '#e2e8f0',
                        borderColor: '#334155',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8,
                        usePointStyle: true,
                        titleFont: {
                            family: 'Inter',
                            size: 13,
                            weight: '600'
                        },
                        bodyFont: {
                            family: 'Inter',
                            size: 12
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(51, 65, 85, 0.2)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: {
                                family: 'Inter',
                                size: 11
                            }
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(51, 65, 85, 0.2)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: {
                                family: 'Inter',
                                size: 11
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                }
            }
        });
    }
}

function showDashProductDropdown() {
    const resultsDiv = document.getElementById('dash-prod-results');
    if (resultsDiv) {
        resultsDiv.style.display = 'block';
        searchDashProducts(document.getElementById('dash-prod-search').value);
    }
}

function searchDashProducts(query) {
    const resultsDiv = document.getElementById('dash-prod-results');
    if (!resultsDiv) return;
    
    const cleanQuery = query.toLowerCase().trim();
    const selectedIds = selectedProducts.map(p => p.id);
    
    const filtered = productsCache.filter(p => {
        const matches = p.name.toLowerCase().includes(cleanQuery) || p.sku.toLowerCase().includes(cleanQuery);
        const notSelected = !selectedIds.includes(p.id);
        return matches && notSelected;
    });
    
    resultsDiv.innerHTML = '';
    
    if (filtered.length === 0) {
        const noResults = document.createElement('div');
        noResults.style.padding = '12px 16px';
        noResults.style.color = 'var(--text-muted)';
        noResults.style.fontSize = '0.9rem';
        noResults.textContent = 'No se encontraron productos';
        resultsDiv.appendChild(noResults);
        return;
    }
    
    filtered.slice(0, 8).forEach(prod => {
        const item = document.createElement('div');
        item.style.padding = '10px 16px';
        item.style.cursor = 'pointer';
        item.style.borderBottom = '1px solid var(--border-glass)';
        item.style.display = 'flex';
        item.style.justifyContent = 'space-between';
        item.style.alignItems = 'center';
        item.style.transition = 'background 0.2s';
        
        item.onmouseover = () => { item.style.background = 'rgba(255, 255, 255, 0.04)'; };
        item.onmouseout = () => { item.style.background = 'transparent'; };
        
        item.onclick = () => {
            addProductFilter(prod);
        };
        
        const textDiv = document.createElement('div');
        textDiv.innerHTML = `<strong style="color: var(--text-main); font-size: 0.9rem;">${prod.name}</strong>`;
        if (prod.sku) {
            textDiv.innerHTML += `<span style="display: block; font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">SKU: ${prod.sku}</span>`;
        }
        
        const addIcon = document.createElement('span');
        addIcon.style.color = 'var(--primary)';
        addIcon.innerHTML = `<i data-lucide="plus" style="width: 16px; height: 16px;"></i>`;
        
        item.appendChild(textDiv);
        item.appendChild(addIcon);
        resultsDiv.appendChild(item);
    });
    
    lucide.createIcons();
}

function addProductFilter(prod) {
    if (selectedProducts.some(p => p.id === prod.id)) return;
    
    selectedProducts.push(prod);
    renderProductTags();
    
    const searchInput = document.getElementById('dash-prod-search');
    if (searchInput) searchInput.value = '';
    
    const resultsDiv = document.getElementById('dash-prod-results');
    if (resultsDiv) resultsDiv.style.display = 'none';
    
    updateDashboardData();
}

function removeProductFilter(prodId) {
    selectedProducts = selectedProducts.filter(p => p.id !== prodId);
    renderProductTags();
    updateDashboardData();
}

function clearProductFilters() {
    selectedProducts = [];
    renderProductTags();
    
    const searchInput = document.getElementById('dash-prod-search');
    if (searchInput) searchInput.value = '';
    
    updateDashboardData();
}

function renderProductTags() {
    const tagsContainer = document.getElementById('selected-products-tags');
    if (!tagsContainer) return;
    
    tagsContainer.innerHTML = '';
    
    selectedProducts.forEach(prod => {
        const tag = document.createElement('span');
        tag.className = 'badge';
        tag.style.background = 'rgba(59, 130, 246, 0.12)';
        tag.style.color = 'var(--primary)';
        tag.style.border = '1px solid rgba(59, 130, 246, 0.3)';
        tag.style.display = 'inline-flex';
        tag.style.alignItems = 'center';
        tag.style.gap = '6px';
        tag.style.padding = '6px 12px';
        tag.style.borderRadius = '20px';
        tag.style.fontSize = '0.85rem';
        
        tag.innerHTML = `
            <span>${prod.name}</span>
            <button style="border: none; background: transparent; cursor: pointer; color: var(--primary); display: inline-flex; align-items: center; padding: 0;" onclick="removeProductFilter(${prod.id})">
                <i data-lucide="x" style="width: 14px; height: 14px;"></i>
            </button>
        `;
        
        tagsContainer.appendChild(tag);
    });
    
    lucide.createIcons();
}

// Inicializar si el canvas del grafico existe
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('salesChart')) {
        initAdminDashboard();
    }
});


