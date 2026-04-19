let currentTableId = null;
let currentFields = [];
let currentTableRecords = [];

window.appIsDirty = false;
window.appLeaveMsg = '¿Seguro que quieres salir? Los cambios no se guardarán.';

async function loadTable(tableId) {
    if (window.appIsDirty) {
        if (!confirm(window.appLeaveMsg)) {
            return; // Abort loadTable
        }
        window.appIsDirty = false;
    }

    // Si no estamos en la vista de tablas, redirigir
    if (!window.location.pathname.includes('tables-view')) {
        window.location.href = `/tables-view#table-${tableId}`;
        return;
    }

    // Cerrar panel de movimientos si está abierto
    const panel = document.getElementById('movement-panel');
    if (panel && panel.classList.contains('open')) {
        closeMovementPanel();
    }

    // Update UI active state safely
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    if (typeof event !== 'undefined' && event && event.currentTarget) {
        if (event.currentTarget.classList) {
            event.currentTarget.classList.add('active');
        }
    }

    // Show table container, hide welcome
    document.getElementById('welcome-screen').style.display = 'none';
    document.getElementById('table-container').style.display = 'flex';

    currentTableId = tableId;

    try {
        const response = await fetch(`/tables/${tableId}`);
        const data = await response.json();

        document.getElementById('current-table-name').innerText = data.name;

        // Mostrar / Ocultar botón de Movimientos
        let btnMovimientos = document.getElementById('btn-movimientos');
        if (btnMovimientos) {
            if (data.name.toLowerCase().includes('inventario')) {
                btnMovimientos.style.display = 'inline-flex';
            } else {
                btnMovimientos.style.display = 'none';
            }
        }

        let btnCreate = document.getElementById('btn-create-row');
        if (btnCreate) {
            let role = typeof currentUserRole !== 'undefined' ? currentUserRole : 'empleado';
            if (['admin', 'manager'].includes(role)) {
                let singularName = data.name.endsWith('s') ? data.name.slice(0, -1) : data.name;
                btnCreate.innerHTML = `<i data-lucide="plus"></i> Añadir ${singularName}`;
                btnCreate.style.display = 'inline-flex';
            } else {
                btnCreate.style.display = 'none';
            }
        }

        currentFields = data.fields;
        currentTableRecords = data.records;
        renderTable(data.fields, data.records);
        lucide.createIcons();
    } catch (e) {
        console.error("Error loading table", e);
    }
}

function renderTable(fields, records) {
    const headRow = document.getElementById('table-head-row');
    const tbody = document.getElementById('table-body');

    // Render Heads
    headRow.innerHTML = '';
    fields.forEach(field => {
        let th = document.createElement('th');
        let role = typeof currentUserRole !== 'undefined' ? currentUserRole : 'empleado';
        if (role === 'admin') {
            actionHtml = `<button class="delete-row-btn" onclick="deleteColumn(${field.id})" style="padding: 0; outline: none; margin-left: 8px;">
                <i data-lucide="x" style="width: 14px; height: 14px;"></i>
            </button>`;
        }

        th.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span>${field.name} <span style="font-size: 0.7em; color: var(--text-muted); text-transform: uppercase;">(${field.field_type})</span></span>
                ${actionHtml}
            </div>
        `;
        headRow.appendChild(th);
    });
    // Add extra column for actions
    let actionTh = document.createElement('th');
    actionTh.style.width = '50px';
    headRow.appendChild(actionTh);

    // Render Body
    tbody.innerHTML = '';
    records.forEach(record => {
        let tr = document.createElement('tr');
        tr.dataset.recordId = record.id;

        // Ensure data is parsed if needed
        let dataObj = record.data || {};
        // Exclude auto-generated fields (COD, ID) from the "new row" detection
        const AUTO_FIELDS = ['COD', 'ID'];
        let isNewRow = !fields.some(f => !AUTO_FIELDS.includes(f.name.toUpperCase()) && dataObj[f.name] !== "" && dataObj[f.name] !== undefined);

        fields.forEach(field => {
            let td = document.createElement('td');
            let val = dataObj[field.name] || '';

            // Render basic input for inline editing
            let isSku = field.name.toUpperCase() === 'COD';
            let isAutoId = field.name.toUpperCase() === 'ID';
            // Los campos auto-generados siempre son texto (el browser ignora strings en type="number")
            let inputType = (isSku || isAutoId) ? 'text'
                : field.field_type === 'number' ? 'number'
                    : field.field_type === 'date' ? 'date'
                        : 'text';

            let inputContainer = document.createElement('div');
            inputContainer.style.position = 'relative';

            let input;

            if (field.field_type === 'select') {
                input = document.createElement('select');
                input.className = 'cell-input input-neumorphic';
                // Añadir una opción vacía por defecto
                let defaultOpt = document.createElement('option');
                defaultOpt.value = "";
                defaultOpt.textContent = "Seleccione...";
                if (!val) defaultOpt.selected = true;
                input.appendChild(defaultOpt);

                if (field.options) {
                    let opts = field.options.split(',');
                    opts.forEach(opt => {
                        let option = document.createElement('option');
                        let trimOpt = opt.trim();
                        option.value = trimOpt;
                        option.textContent = trimOpt;
                        if (val === trimOpt) option.selected = true;
                        input.appendChild(option);
                    });
                }
                
                if (!isNewRow) {
                    input.disabled = true; // select usa disabled, no readOnly
                    input.classList.add('locked-input');
                }
            } else {
                input = document.createElement('input');
                input.type = inputType;
                input.value = val;
                input.className = 'cell-input';
                if (isSku || isAutoId) {
                    input.readOnly = true;
                    input.title = "Generado automáticamente";
                    input.classList.add('locked-input');
                    input.style.cursor = 'default';
                    input.style.color = 'var(--text-muted)';
                    input.style.fontStyle = 'italic';
                } else {
                    if (!isNewRow) {
                        input.readOnly = true;
                        input.classList.add('locked-input');
                    }
                }

                if (field.name.toUpperCase() === 'UNIDAD DE VENTA' || field.name.toUpperCase() === 'UNIDAD') {
                    input.setAttribute('list', 'unidades-list');
                    input.placeholder = "Buscar unidad...";
                } else if (field.options) {
                    let datalistId = 'list-' + field.id + '-' + record.id;
                    input.setAttribute('list', datalistId);
                    input.placeholder = "Opciones disponibles...";

                    let datalist = document.createElement('datalist');
                    datalist.id = datalistId;
                    let opts = field.options.split(',');
                    opts.forEach(opt => {
                        let option = document.createElement('option');
                        option.value = opt.trim();
                        datalist.appendChild(option);
                    });
                    inputContainer.appendChild(datalist);
                }
            }

            // Empty state UX
            if (!val && !isSku && !isAutoId && input.tagName !== 'SELECT') {
                input.classList.add('empty-cell');
                let placeholder = document.createElement('span');
                placeholder.className = 'empty-placeholder';
                placeholder.innerHTML = '⚠️ Vacío, clic para editar';
                inputContainer.appendChild(placeholder);

                input.addEventListener('focus', () => {
                    placeholder.style.display = 'none';
                    input.classList.remove('empty-cell');
                });
                input.addEventListener('blur', () => {
                    if (!input.value) {
                        placeholder.style.display = 'flex';
                        input.classList.add('empty-cell');
                    }
                });
            }

            // Removed save on blur for explicit save button experience
            // Or save on enter
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.target.blur();
                    saveRow(record.id);
                }
            });

            // Progressive Disclosure Logic
            input.addEventListener('input', () => updateRowProgressive(tr));

            inputContainer.appendChild(input);
            td.appendChild(inputContainer);
            tr.appendChild(td);
        });

        // Action td
        let actionTd = document.createElement('td');
        actionTd.style.whiteSpace = 'nowrap';
        let role = typeof currentUserRole !== 'undefined' ? currentUserRole : 'empleado';
        let deleteRowHtml = '';
        if (['admin', 'manager'].includes(role)) {
            deleteRowHtml = `<button class="delete-row-btn" onclick="deleteRow(${record.id})" title="Eliminar Fila"><i data-lucide="trash-2"></i></button>`;
        }

        let actionBtnHtml = `
            <button class="btn btn-primary action-btn save-btn" onclick="saveRow(${record.id})" style="padding: 6px 12px; margin-right: 8px; font-size: 0.8rem;" title="Guardar Fila">
                <i data-lucide="save" style="width: 14px;"></i> Guardar
            </button>
        `;
        if (!isNewRow) {
            actionBtnHtml = `
                <button class="btn btn-secondary action-btn edit-btn" onclick="enableEditRow(${record.id}, this)" style="padding: 6px 12px; margin-right: 8px; font-size: 0.8rem;" title="Editar Fila">
                    <i data-lucide="edit" style="width: 14px;"></i> Editar
                </button>
            `;
        }

        actionTd.innerHTML = `
            ${actionBtnHtml}
            ${deleteRowHtml}
        `;
        tr.appendChild(actionTd);

        tbody.appendChild(tr);

        // Initial run to lock upcoming empty cells
        updateRowProgressive(tr);
    });

    lucide.createIcons();
}

function updateRowProgressive(tr) {
    let allInputs = tr.querySelectorAll('.cell-input');
    let previousFilled = true;

    allInputs.forEach(input => {
        if (input.title === "Generado automáticamente") return; // Ignorar campos auto-generados (COD, ID)

        let container = input.parentElement;
        let placeholder = container.querySelector('.empty-placeholder');

        if (!previousFilled) {
            input.disabled = true;
            input.style.opacity = '0'; // Totalmente invisible hasta que le toque
            container.style.opacity = '0.3';
            if (placeholder) placeholder.style.display = 'none';
        } else {
            input.disabled = false;
            input.style.opacity = '1';
            container.style.opacity = '1';

            if (input.value.trim() === '') {
                previousFilled = false; // La cadena se rompe aquí
                if (placeholder && document.activeElement !== input) {
                    placeholder.style.display = 'flex';
                }
            } else {
                if (placeholder) placeholder.style.display = 'none';
            }
        }
    });
}

window.enableEditRow = function (recordId, btn) {
    let tr = document.querySelector(`tr[data-record-id="${recordId}"]`);
    if (!tr) return;

    let inputs = tr.querySelectorAll('.cell-input:not([title="Generado automáticamente"])');
    inputs.forEach(inp => {
        inp.readOnly = false;
        inp.disabled = false; // Desbloquea también los elementos select
        inp.classList.remove('locked-input');
    });

    if (inputs.length > 0) inputs[0].focus();

    btn.outerHTML = `
        <button class="btn btn-primary action-btn save-btn" onclick="saveRow(${recordId})" style="padding: 6px 12px; margin-right: 8px; font-size: 0.8rem;" title="Guardar Fila">
            <i data-lucide="save" style="width: 14px;"></i> Guardar
        </button>
    `;
    lucide.createIcons();
}

// ---- Record Actions ----

async function addRow() {
    if (!currentTableId) return;

    // Bloquear si ya hay una fila nueva sin guardar
    const pendingSaveBtn = document.querySelector('#table-body .save-btn');
    if (pendingSaveBtn) {
        alert("Completa y guarda la fila actual antes de crear una nueva.");
        const firstInput = pendingSaveBtn.closest('tr')?.querySelector('.cell-input:not([title="Generado automáticamente"])');
        if (firstInput) firstInput.focus();
        return;
    }

    // Create an empty payload string based on current fields
    let initialData = {};
    currentFields.forEach(f => {
        initialData[f.name] = "";
    });

    try {
        await fetch(`/records/${currentTableId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: initialData })
        });
        // Reload silently
        loadTableSilently();
    } catch (e) {
        console.error("Failed to add row", e);
    }
}

async function deleteRow(recordId) {
    if (!confirm("¿Seguro que deseas eliminar esta fila?")) return;
    try {
        await fetch(`/records/${recordId}`, { method: 'DELETE' });
        loadTableSilently();
    } catch (e) {
        console.error("Failed to delete row", e);
    }
}

// Función para guardar toda la fila bajo demanda manual
async function saveRow(recordId) {
    let tr = document.querySelector(`tr[data-record-id="${recordId}"]`);
    if (!tr) return;

    console.log(`Guardando fila: ${recordId}`);

    let updatedData = {};
    let inputs = tr.querySelectorAll('.cell-input');
    let isValid = true;

    currentFields.forEach((f, idx) => {
        let type = inputs[idx].type;
        let val = inputs[idx].value;

        // Validación Anti-Vacíos (excluir campos auto-generados)
        const AUTO_FIELDS_SAVE = ['COD', 'ID'];
        if (String(val).trim() === '' && !AUTO_FIELDS_SAVE.includes(f.name.toUpperCase())) {
            alert(`El campo "${f.name}" es obligatorio y no puede quedar vacío.`);
            isValid = false;
        }

        if (type === 'number' && val !== '') val = Number(val);
        updatedData[f.name] = val;
    });

    if (!isValid) {
        loadTableSilently(); // Revert visual state
        return;
    }

    let saveBtn = tr.querySelector('.save-btn');
    if (saveBtn) {
        saveBtn.innerHTML = '<i data-lucide="loader" class="spin"></i> Cargando...';
        saveBtn.style.opacity = '0.7';
    }

    try {
        await fetch(`/records/${recordId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: updatedData })
        });

        // Efecto visual de guardado exitoso
        inputs.forEach(input => {
            input.style.backgroundColor = 'rgba(16, 185, 129, 0.15)'; // Verde sutil
            setTimeout(() => input.style.backgroundColor = 'transparent', 800);
        });

        if (saveBtn) {
            saveBtn.style.backgroundColor = 'var(--success)';
            saveBtn.innerHTML = '<i data-lucide="check" style="width: 14px;"></i> Listo';
            saveBtn.style.opacity = '1';
            
            // Esperar un momento para que el usuario vea el "Listo" y luego refrescar la fila
            setTimeout(() => {
                loadTableSilently();
            }, 600);
        } else {
            loadTableSilently();
        }
    } catch (e) {
        console.error("Failed to save row", e);
        loadTableSilently();
    }
}


// ---- Column Actions (No Code builder) ----

function showAddColumnModal() {
    document.getElementById('add-column-modal').classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
    const nameEl = document.getElementById('new-col-name');
    const optEl = document.getElementById('new-col-options');
    if (nameEl) nameEl.value = '';
    if (optEl) optEl.value = '';
}

async function submitNewColumn() {
    if (!currentTableId) return;

    let colName = document.getElementById('new-col-name').value.trim();
    let colType = document.getElementById('new-col-type').value;
    let colOptions = document.getElementById('new-col-options')?.value.trim() || null;

    if (!colName) {
        alert("El nombre de la columna no puede estar vacío");
        return;
    }

    try {
        await fetch(`/tables/${currentTableId}/fields`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: colName, field_type: colType, options: colOptions || null })
        });

        closeModal('add-column-modal');
        loadTableSilently();
    } catch (e) {
        console.error("Failed to add column", e);
    }
}

// Oculta/Muestra las opciones sugeridas según el tipo elegido
window.toggleSuggestedOptions = function(selectEl) {
    const parentContainer = selectEl.closest('div[style]').parentElement;
    const optionsContainer = parentContainer.querySelector('.options-container');
    if (optionsContainer) {
        const input = optionsContainer.querySelector('input');
        if (selectEl.value === 'select') {
            input.readOnly = false;
            input.style.opacity = '1';
            input.style.pointerEvents = 'auto';
            input.placeholder = 'Escribe las opciones (Ej: A, B, C)';
        } else {
            input.readOnly = true;
            input.style.opacity = '0.7';
            input.style.pointerEvents = 'none';
            input.placeholder = 'Opciones sugeridas...';
        }
    }
};

// ── Estado local del reordenamiento (solo se aplica al guardar) ──────────────
let _pendingFieldOrder = null; // null = no hay orden pendiente

function openManageColumnsModal() {
    if (!currentTableId) return alert("Selecciona una tabla primero.");

    _pendingFieldOrder = null; // reset al abrir

    const list = document.getElementById('manage-columns-list');
    list.innerHTML = '';

    // Resetear botón por si quedó en estado anterior
    const saveBtn = document.getElementById('btn-save-all-cols');
    saveBtn.style.background = '';
    saveBtn.innerHTML = '<i data-lucide="save"></i> Guardar';
    saveBtn.disabled = false;

    let dragSrc = null;

    currentFields.forEach((field) => {
        const card = document.createElement('div');
        card.style.cssText = 'display:flex; gap:10px; align-items:center; background:var(--secondary); padding:12px; border-radius:10px; flex-wrap:wrap; cursor:default; transition: border-top 0.1s;';
        card.dataset.fieldId = field.id;
        card.draggable = true;

        card.innerHTML = `
            <div style="cursor:grab; color:var(--text-muted); padding:0 4px; display:flex; align-items:center;" title="Arrastra para reordenar">
                <i data-lucide="grip-vertical" style="width:18px;"></i>
            </div>
            <div style="flex:1; min-width:120px;">
                <label style="font-size:0.75rem; color:var(--text-muted); display:block; margin-bottom:4px;">Nombre</label>
                <input type="text" value="${field.name}" class="input-neumorphic col-edit-name"
                       data-field-id="${field.id}" style="width:100%; padding:8px;">
            </div>
            <div style="width:130px;">
                <label style="font-size:0.75rem; color:var(--text-muted); display:block; margin-bottom:4px;">Tipo</label>
                <select class="input-neumorphic col-edit-type" data-field-id="${field.id}" style="width:100%; padding:8px;" onchange="window.toggleSuggestedOptions(this)">
                    <option value="text"   ${field.field_type === 'text' ? 'selected' : ''}>Texto</option>
                    <option value="number" ${field.field_type === 'number' ? 'selected' : ''}>Número</option>
                    <option value="date"   ${field.field_type === 'date' ? 'selected' : ''}>Fecha</option>
                    <option value="select" ${field.field_type === 'select' ? 'selected' : ''}>Selección</option>
                </select>
            </div>
            <div class="options-container" style="flex:1; min-width:140px;">
                <label style="font-size:0.75rem; color:var(--text-muted); display:block; margin-bottom:4px;">Opciones / Sugerencias</label>
                <input type="text" value="${field.options || ''}" class="input-neumorphic col-edit-options"
                       data-field-id="${field.id}" placeholder="${field.field_type === 'select' ? 'Escribe las opciones (Ej: A, B, C)' : 'Opciones sugeridas...'}" 
                       style="width:100%; padding:8px; ${field.field_type !== 'select' ? 'opacity:0.7; pointer-events:none;' : ''}" ${field.field_type !== 'select' ? 'readonly' : ''}>
            </div>
            <div style="display:flex; align-items:center; padding-top:18px;">
                <button onclick="deleteColumnFromModal(${field.id})" class="btn" style="padding:6px 10px; font-size:0.8rem; background:transparent; color:var(--danger); border:1px solid var(--danger);" title="Eliminar columna">
                    <i data-lucide="trash-2" style="width:13px;"></i>
                </button>
            </div>
        `;

        // ── Drag & Drop (solo reordena en el DOM, no llama al backend aún) ──
        card.addEventListener('dragstart', (e) => {
            dragSrc = card;
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', String(field.id));
            setTimeout(() => card.style.opacity = '0.4', 0);
        });

        card.addEventListener('dragend', () => {
            card.style.opacity = '1';
            list.querySelectorAll('[data-field-id]').forEach(c => c.style.borderTop = '');
        });

        card.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            list.querySelectorAll('[data-field-id]').forEach(c => c.style.borderTop = '');
            if (card !== dragSrc) card.style.borderTop = '2px solid var(--primary)';
        });

        card.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            list.querySelectorAll('[data-field-id]').forEach(c => c.style.borderTop = '');

            if (dragSrc && dragSrc !== card) {
                const cards = [...list.children];
                const srcIdx = cards.indexOf(dragSrc);
                const tgtIdx = cards.indexOf(card);
                if (srcIdx < tgtIdx) {
                    list.insertBefore(dragSrc, card.nextSibling);
                } else {
                    list.insertBefore(dragSrc, card);
                }
                // Marcar orden pendiente (se aplica solo al guardar)
                _pendingFieldOrder = [...list.children].map((c, i) => ({
                    id: parseInt(c.dataset.fieldId),
                    order_index: i
                }));
            }
            dragSrc = null;
        });

        list.appendChild(card);
    });

    lucide.createIcons();
    document.getElementById('manage-columns-modal').classList.add('active');
}

async function deleteColumnFromModal(fieldId) {
    if (!confirm("¿Seguro que deseas eliminar esta columna? Los datos de las filas no se perderán pero dejarán de mostrarse.")) return;
    try {
        await fetch(`/fields/${fieldId}`, { method: 'DELETE' });
        document.getElementById('manage-columns-modal').classList.remove('active');
        _pendingFieldOrder = null;
        loadTableSilently();
    } catch (e) {
        console.error("Failed to delete column", e);
    }
}

async function saveAllColumns() {
    const btn = document.getElementById('btn-save-all-cols');
    const cards = [...document.querySelectorAll('#manage-columns-list > [data-field-id]')];

    if (cards.length === 0) return;

    // Validar nombres
    for (const card of cards) {
        const nameInput = card.querySelector('.col-edit-name');
        if (nameInput && !nameInput.value.trim()) {
            nameInput.style.borderColor = 'var(--danger)';
            nameInput.focus();
            alert("Hay columnas sin nombre. Completa todos los campos antes de guardar.");
            return;
        }
        if (nameInput) nameInput.style.borderColor = '';
    }

    btn.innerHTML = '<i data-lucide="loader" class="spin"></i> Guardando...';
    btn.disabled = true;
    lucide.createIcons();

    try {
        // Guardar cada campo secuencialmente con verificación de respuesta
        for (const card of cards) {
            const fieldId = parseInt(card.dataset.fieldId);
            const name = card.querySelector(`.col-edit-name[data-field-id="${fieldId}"]`).value.trim();
            const type = card.querySelector(`.col-edit-type[data-field-id="${fieldId}"]`).value;
            const options = card.querySelector(`.col-edit-options[data-field-id="${fieldId}"]`).value.trim();

            const res = await fetch(`/fields/${fieldId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, field_type: type, options: options || null })
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `Error al guardar campo #${fieldId} (${res.status})`);
            }
        }

        // Guardar reordenamiento pendiente si existe
        if (_pendingFieldOrder) {
            const res = await fetch(`/tables/${currentTableId}/reorder-fields`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fields: _pendingFieldOrder })
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `Error al guardar el orden (${res.status})`);
            }
        }

        // ✅ Éxito: animación corta → cerrar modal
        btn.style.background = 'var(--success)';
        btn.innerHTML = '<i data-lucide="check"></i> ¡Guardado!';
        lucide.createIcons();

        setTimeout(() => {
            document.getElementById('manage-columns-modal').classList.remove('active');
            btn.style.background = '';
            btn.innerHTML = '<i data-lucide="save"></i> Guardar';
            btn.disabled = false;
            _pendingFieldOrder = null;
            lucide.createIcons();
            loadTableSilently();
        }, 1500);

    } catch (e) {
        console.error('saveAllColumns error:', e);
        alert('No se pudieron guardar los cambios:\n' + e.message);
        btn.style.background = 'var(--danger)';
        btn.innerHTML = '<i data-lucide="x"></i> Error';
        btn.disabled = false;
        lucide.createIcons();
        setTimeout(() => {
            btn.style.background = '';
            btn.innerHTML = '<i data-lucide="save"></i> Guardar';
            lucide.createIcons();
        }, 2000);
    }
}


async function deleteColumn(fieldId) {
    if (!confirm("¿Seguro que deseas eliminar esta columna? Los datos existentes en las filas no se perderán pero dejarán de mostrarse.")) return;

    try {
        await fetch(`/fields/${fieldId}`, { method: 'DELETE' });
        loadTableSilently();
    } catch (e) {
        console.error("Failed to delete column", e);
    }
}

async function deleteCurrentTable() {
    if (!currentTableId) return;
    const tableName = document.getElementById('current-table-name').innerText;
    if (tableName.toLowerCase() === 'inventario') {
        if (!confirm(`⚠️ ADVERTENCIA CRÍTICA: "Inventario" es la tabla base. ¿Estás absolutamente seguro de eliminarla?`)) return;
    } else {
        if (!confirm(`¿Seguro que deseas eliminar permanentemente la tabla "${tableName}" y TODOS sus datos?`)) return;
    }

    try {
        const res = await fetch(`/tables/${currentTableId}`, { method: 'DELETE' });
        if (res.ok) {
            alert("Tabla eliminada con éxito.");
            window.location.href = "/dashboard";
        } else {
            const data = await res.json();
            alert("Error: " + data.detail);
        }
    } catch (e) {
        console.error("Falló la eliminación de la tabla", e);
    }
}

// Helper to refresh without resetting active menu
async function loadTableSilently() {
    try {
        const response = await fetch(`/tables/${currentTableId}`);
        const data = await response.json();
        currentFields = data.fields;
        currentTableRecords = data.records;
        renderTable(data.fields, data.records);
    } catch (e) {
        console.error("Error refreshing table", e);
    }
}

// ---- Theme Logic ----
function toggleTheme() {
    let isDark;
    if (document.body.classList.contains('dark-theme')) {
        document.body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
        isDark = false;
    } else {
        document.body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
        isDark = true;
    }

    let toggleSettings = document.getElementById('theme-toggle-settings');
    if (toggleSettings) toggleSettings.checked = isDark;
}

// ---- Zoom / Customization Logic ----
let currentZoomDelta = parseInt(localStorage.getItem('zoomDelta')) || 0;
applyZoom();

function changeZoom(delta) {
    currentZoomDelta += delta;
    if (currentZoomDelta < -3) currentZoomDelta = -3;
    if (currentZoomDelta > 5) currentZoomDelta = 5; // Limite max 150%
    localStorage.setItem('zoomDelta', currentZoomDelta);
    applyZoom();
}

function applyZoom() {
    let zoomLevel = 1 + (currentZoomDelta * 0.1);
    document.body.style.zoom = zoomLevel;

    let display = document.getElementById('zoom-level-display');
    if (display) {
        display.innerText = Math.round(zoomLevel * 100) + '%';
    }
}

// ---- Movement / POS Logic ----
let cartItems = {};

async function loadClientsDatalist() {
    try {
        const res = await fetch('/api/clients/suggest');
        if (!res.ok) return;
        const clients = await res.json();
        const dl = document.getElementById('clients-sug');
        if (dl) {
            dl.innerHTML = '';
            clients.forEach(c => {
                let opt = document.createElement('option');
                opt.value = c;
                dl.appendChild(opt);
            });
        }
    } catch (e) { }
}

function openMovementPanel() {
    const tableName = document.getElementById('current-table-name').innerText.toLowerCase();
    if (!tableName.includes('inventario')) {
        return alert("El panel de movimientos está diseñado para usarlo en el Inventario para calcular cantidades automáticamente.");
    }
    document.getElementById('movement-panel').classList.add('open');
    document.getElementById('inventory-search').value = '';
    document.getElementById('search-results').innerHTML = '';
    loadClientsDatalist();
    renderCart();
}

function closeMovementPanel() {
    document.getElementById('movement-panel').classList.remove('open');
}

function searchInventory() {
    const q = document.getElementById('inventory-search').value.toLowerCase();
    const resDiv = document.getElementById('search-results');
    resDiv.innerHTML = '';
    if (!q) return;

    const results = currentTableRecords.filter(r => {
        let name = r.data.Nombre || '';
        let sku = r.data.COD || '';
        return name.toLowerCase().includes(q) || sku.toLowerCase().includes(q);
    });

    results.forEach(r => {
        let div = document.createElement('div');
        div.className = 'search-item';
        div.style.padding = '8px 12px';
        div.style.background = 'var(--bg-dark)';
        div.style.borderBottom = '1px solid var(--border-glass)';
        div.style.cursor = 'pointer';
        div.innerHTML = `<span>${r.data.Nombre} <small style="color:var(--text-muted)">${r.data.COD || ''}</small></span> <span style="font-weight:bold; color:var(--primary)">${r.data.Cantidad || 0} disp.</span>`;
        div.onclick = () => addToCart(r);
        resDiv.appendChild(div);
    });
}

function addToCart(record) {
    if (!cartItems[record.id]) {
        cartItems[record.id] = { record, qty: 1 };
    } else {
        cartItems[record.id].qty += 1;
    }
    document.getElementById('inventory-search').value = '';
    searchInventory();
    renderCart();
}

function updateCartQty(id, change) {
    if (cartItems[id]) {
        cartItems[id].qty += change;
        if (cartItems[id].qty <= 0) {
            delete cartItems[id]; // remover si llega a 0
        }
    }
    renderCart();
}

function toggleMovementType() {
    let typeEl = document.querySelector('input[name="mov-type"]:checked');
    let type = typeEl ? typeEl.value : "Venta";

    let clientLabel = document.getElementById('lbl-mov-client');
    let financials = document.getElementById('cart-financials');
    let btnProcess = document.getElementById('btn-process-mov');

    if (type === "Venta") {
        clientLabel.innerHTML = `<i data-lucide="user" style="width: 12px; margin-right: 4px;"></i> Destinatario / Cliente (Opcional)`;
        financials.style.display = 'block';
        btnProcess.innerText = "Procesar Cobro";
        btnProcess.className = "btn btn-primary btn-block";
    } else {
        clientLabel.innerHTML = `<i data-lucide="truck" style="width: 12px; margin-right: 4px;"></i> Origen / Proveedor (Opcional)`;
        financials.style.display = 'none'; // Al comprar mercadería, el costo difiere del precio de venta, no se asume
        btnProcess.innerText = "Registrar Ingreso de Stock";
        btnProcess.className = "btn btn-warning btn-block";
    }
    lucide.createIcons();
    renderCart(); // Re-render to hide/show price items
}

function renderCart() {
    const c = document.getElementById('cart-items');
    c.innerHTML = '';

    let total = 0;
    let typeEl = document.querySelector('input[name="mov-type"]:checked');
    let type = typeEl ? typeEl.value : "Venta";

    Object.values(cartItems).forEach(item => {
        let div = document.createElement('div');
        div.className = 'cart-item';

        // Soporte para "Precio" o "Precio por Unidad"
        let precioVal = item.record.data['Precio por Unidad'] || item.record.data['Precio'] || item.record.data['precio'] || 0;
        let precio = parseFloat(precioVal) || 0;
        let subtotalFila = precio * item.qty;
        total += subtotalFila;

        let pricingHtml = '';
        if (type === "Venta") {
            pricingHtml = `<small style="color:var(--success)">$${precio.toFixed(2)} c/u (Sub: $${subtotalFila.toFixed(2)})</small>`;
        }

        div.innerHTML = `
            <div style="flex: 1;">
                <strong>${item.record.data.Nombre}</strong><br>
                <small>${item.record.data.COD} | Disp: ${item.record.data.Cantidad}</small><br>
                ${pricingHtml}
            </div>
            <div class="qty-controls">
                <button class="qty-btn" onclick="updateCartQty(${item.record.id}, -1)">-</button>
                <span style="min-width: 24px; text-align:center; font-weight: bold;">${item.qty}</span>
                <button class="qty-btn" onclick="updateCartQty(${item.record.id}, 1)">+</button>
            </div>
        `;
        c.appendChild(div);
    });

    // Desglose de Facturación
    let subtotalSinIva = total / 1.15;
    let iva = total - subtotalSinIva;

    document.getElementById('cart-subtotal').innerText = `$${subtotalSinIva.toFixed(2)}`;
    document.getElementById('cart-iva').innerText = `$${iva.toFixed(2)}`;
    document.getElementById('cart-total').innerText = `$${total.toFixed(2)}`;
}

async function processMovement() {
    let typeEl = document.querySelector('input[name="mov-type"]:checked');
    let type = typeEl ? typeEl.value : "Venta";
    let clientName = document.getElementById('mov-client').value.trim();

    let payload = Object.values(cartItems).map(i => ({ record_id: i.record.id, quantity_change: i.qty }));
    if (payload.length === 0) return alert("Ponga elementos de inventario en el panel para registrar.");

    let totalText = document.getElementById('cart-total').textContent.replace('$', '');
    let subtotalText = document.getElementById('cart-subtotal').textContent.replace('$', '');
    let ivaText = document.getElementById('cart-iva').textContent.replace('$', '');

    try {
        const res = await fetch('/inventory/movement', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: type,
                client_name: clientName,
                subtotal: parseFloat(subtotalText),
                iva: parseFloat(ivaText),
                total: parseFloat(totalText),
                items: payload
            })
        });
        if (res.ok) {
            cartItems = {};
            document.getElementById('mov-client').value = '';
            closeMovementPanel();
            loadTableSilently();
            alert(`¡${type} procesada con éxito! El movimiento quedó registrado integralmente en la base de datos de Auditoría.`);
        }
    } catch (e) {
        console.error(e);
    }
}

// ---- Table Search Filter ----
function filterTables() {
    const q = document.getElementById('table-search').value.toLowerCase();
    const items = document.querySelectorAll('.table-item');
    items.forEach(item => {
        const textElement = item.querySelector('.table-name-text');
        if (!textElement) return;
        const text = textElement.innerText.toLowerCase();
        if (text.includes(q)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// ---- Audits / Historial ----
async function openAuditsModal() {
    document.getElementById('audits-modal').style.display = 'flex';
    const tbody = document.getElementById('audits-table-body');
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">Cargando historial...</td></tr>';

    try {
        const res = await fetch('/api/audits');
        const audits = await res.json();
        tbody.innerHTML = '';

        if (audits.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No hay registros aún.</td></tr>';
            return;
        }

        audits.forEach(a => {
            let tr = document.createElement('tr');

            // Si la acción incluye Venta o Compra, resaltamos visualmente el recuadro
            let actionHtml = a.action;
            if (a.action.includes('Venta |')) {
                actionHtml = `<span style="color: var(--success); font-weight: bold;">${a.action}</span>`;
            } else if (a.action.includes('Compra |')) {
                actionHtml = `<span style="color: var(--warning); font-weight: bold;">${a.action}</span>`;
            }

            // Simple fecha formateada legible
            let dateStr = "N/A";
            if (a.timestamp !== "N/A") {
                let d = new Date(a.timestamp);
                dateStr = d.toLocaleString();
            }

            tr.innerHTML = `
                <td>#${a.id}</td>
                <td><span class="badge" style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px;">${a.employee_code || '?'}</span></td>
                <td>${actionHtml}</td>
                <td style="font-size: 0.85em; color: var(--text-muted);">${dateStr}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--danger);">Error al cargar historial</td></tr>';
    }
}

// ---- Authentication ----

async function checkEmail() {
    const email = document.getElementById('email-input').value;
    if (!email) return alert("Por favor ingresa un correo");
    if (!email.includes('@')) return alert("El correo debe llevar '@'");

    try {
        const res = await fetch('/auth/check-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();

        if (data.exists) {
            document.getElementById('step-email').style.display = 'none';
            document.getElementById('step-password').style.display = 'block';
            document.getElementById('footer-default').style.display = 'block';
        } else {
            document.getElementById('footer-default').style.display = 'none';
            alert("El correo no está registrado. Puedes registrarte debajo.");
        }
    } catch (e) {
        console.error(e);
    }
}

function backToEmail() {
    document.getElementById('step-password').style.display = 'none';
    document.getElementById('step-email').style.display = 'block';
    document.getElementById('password-input').value = '';
}

async function login() {
    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;
    if (!password) return alert("Ingresa tu contraseña");

    try {
        const res = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        if (res.ok) {
            window.location.href = "/dashboard";
        } else {
            const err = await res.json();
            alert("Error: " + (err.detail || "Credenciales inválidas"));
        }
    } catch (e) {
        console.error(e);
    }
}

async function checkRegisterEmail() {
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    if (!name || !email) return alert("Por favor ingresa nombre y correo");
    if (!email.includes('@')) return alert("El correo debe llevar '@'");

    try {
        const res = await fetch('/auth/check-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();

        if (data.exists) {
            alert("El correo ya está registrado con otra cuenta.");
        } else {
            document.getElementById('reg-step-1').style.display = 'none';
            document.getElementById('reg-step-2').style.display = 'block';
        }
    } catch (e) {
        console.error(e);
    }
}

function showConfirmPass() {
    const pass = document.getElementById('reg-pass').value;
    if (!pass) return alert("Ingresa una contraseña");

    document.getElementById('reg-step-2').style.display = 'none';
    document.getElementById('reg-step-3').style.display = 'block';
}

function backToRegStep(step) {
    document.getElementById('reg-step-1').style.display = 'none';
    document.getElementById('reg-step-2').style.display = 'none';
    document.getElementById('reg-step-3').style.display = 'none';
    document.getElementById(`reg-step-${step}`).style.display = 'block';
}

async function registerUser() {
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-pass').value;
    const confirm = document.getElementById('reg-confirm').value;
    const role = document.getElementById('reg-role').value;

    if (!name || !email || !password) return alert("Llena todos los campos");
    if (password !== confirm) return alert("Las contraseñas no coinciden");

    try {
        const res = await fetch('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, full_name: name, password, role })
        });
        if (res.ok) {
            const btnVolver = document.querySelector('button[onclick*="/dashboard"]');
            if (btnVolver) {
                alert("¡Usuario registrado con éxito como " + role + "!");
                window.location.reload(); // Reiniciar formulario
            } else {
                window.location.href = "/dashboard";
            }
        } else {
            const err = await res.json();
            alert("Error: " + (err.detail || "No se pudo registrar"));
        }
    } catch (e) {
        console.error(e);
    }
}

async function logout() {
    try {
        await fetch('/auth/logout', { method: 'POST' });
        window.location.href = "/login";
    } catch (e) {
        console.error(e);
    }
}

// Al cargar la página, si hay un hash #table-X, cargar esa tabla automáticamente
// (pasa cuando se redirige desde otra página al hacer clic en una tabla del sidebar)
function checkHashAndLoadTable() {
    if (window.location.pathname.includes('tables-view')) {
        const hash = window.location.hash; // ej: "#table-3"
        const match = hash.match(/#table-(\d+)/); // más flexible sin ^ y $
        if (match) {
            const tableId = match[1];
            // Limpiar el hash para que no quede en la URL
            history.replaceState(null, '', window.location.pathname);
            // Cargar la tabla
            loadTable(tableId);
            // Marcar activo en el sidebar
            setTimeout(() => {
                document.querySelectorAll(`.nav-link[data-table-id="${tableId}"]`).forEach(l => {
                    l.classList.add('active');
                });
            }, 100);
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkHashAndLoadTable);
} else {
    checkHashAndLoadTable();
}
