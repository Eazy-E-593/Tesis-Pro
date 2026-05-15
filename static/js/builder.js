document.addEventListener('DOMContentLoaded', () => {
    const draggables = document.querySelectorAll('.draggable-item');
    const dropZone = document.getElementById('drop-zone');
    let fieldCount = 0;
    let draggedData = null;

    window.appIsDirty = false; // true cuando hay campos en el canvas sin guardar
    window.appLeaveMsg = '¿Seguro que quieres salir? Los cambios del constructor no se guardarán.';

    // Interceptar navegación del browser (F5, cerrar tab, escribir URL)
    window.addEventListener('beforeunload', (e) => {
        if (window.appIsDirty) {
            e.preventDefault();
            e.returnValue = window.appLeaveMsg;
        }
    });



    // ── Sidebar items: dragstart / dragend / click ───────────────────────────
    draggables.forEach(draggable => {
        draggable.addEventListener('dragstart', (e) => {
            const dataObj = {
                type: draggable.dataset.type,
                label: draggable.querySelector('span').innerText,
                icon: draggable.dataset.icon || 'type'
            };
            draggedData = dataObj;
            e.dataTransfer.effectAllowed = 'copy';
            e.dataTransfer.setData('text/plain', JSON.stringify(dataObj));
            draggable.classList.add('dragging');
        });

        draggable.addEventListener('dragend', () => {
            draggable.classList.remove('dragging');
        });

        // Click como alternativa táctil / accesible
        draggable.addEventListener('click', () => {
            addFieldToCanvas(
                draggable.dataset.type,
                draggable.querySelector('span').innerText,
                draggable.dataset.icon || 'type'
            );
        });
    });

    // ── Document-level dragover ───────────────────────────────────────────────
    // Usamos stopPropagation y preventDefault en dragenter y dragover 
    // para indicar al navegador que este elemento es definitivamente un objetivo de drop válido.
    dropZone.addEventListener('dragenter', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('drop-zone-active');
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.dataTransfer.dropEffect = 'copy';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!dropZone.contains(e.relatedTarget)) {
            dropZone.classList.remove('drop-zone-active');
        }
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drop-zone-active');

        let parsedData = null;
        try {
            let dataStr = e.dataTransfer.getData('text/plain');
            if (dataStr) {
                // If the user drops pure text from somewhere else, it might fail here, which is fine
                parsedData = JSON.parse(dataStr);
            }
        } catch (err) {
            console.error("Error parsing drag data, using fallback", err);
        }

        if (parsedData && parsedData.type) {
            addFieldToCanvas(parsedData.type, parsedData.label, parsedData.icon);
        } else if (draggedData) {
            addFieldToCanvas(draggedData.type, draggedData.label, draggedData.icon);
        }

        // Clean up
        draggedData = null;
    });

    // ── Agregar tarjeta al canvas ─────────────────────────────────────────────
    function addFieldToCanvas(type, label, iconName) {
        window.appIsDirty = true; // marcar como modificado
        // Limpieza de campos vacíos antes de agregar uno nuevo
        const existingCards = dropZone.querySelectorAll('.field-config-card');
        existingCards.forEach(card => {
            const nameInput = card.querySelector('.field-name-input');
            if (nameInput && nameInput.value.trim() === '') {
                card.remove();
            }
        });

        fieldCount++;

        const emptyState = dropZone.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        const fieldCard = document.createElement('div');
        fieldCard.className = 'field-config-card glass-panel';
        fieldCard.dataset.type = type;
        fieldCard.id = `field-${fieldCount}`;

        // Sugerencias pre-llenadas por tipo de campo
        const SUGGESTED_OPTIONS = {
            'text': 'Nombre, Email, Dirección',
            'number': '0, 10, 100',
            'date': 'Fecha de Ingreso, Fecha de Despido',
            'select': ''
        };
        const defaultOptions = SUGGESTED_OPTIONS[type] || '';
        const isSelect = type === 'select';

        const hintHtml = isSelect
            ? `<div class="field-options-group">
                 <label>Opciones de selección:</label>
                 <input type="text" class="field-options-input input-neumorphic" 
                        placeholder="Ej: Aprobado, Rechazado (separadas por coma)" 
                        value="${defaultOptions}">
               </div>`
            : `<div class="field-hint">
                 <i data-lucide="lightbulb" style="width: 14px;"></i>
                 <span><strong>Sugerencia:</strong> ${defaultOptions}</span>
               </div>`;

        fieldCard.innerHTML = `
            <div class="field-drag-handle">
                <i data-lucide="grip-vertical"></i>
            </div>
            <div class="field-info">
                <div class="field-type-badge">
                    <i data-lucide="${iconName}" style="width: 14px;"></i> ${label}
                </div>
                <div class="field-options-group">
                    <label>Nombre de la columna:</label>
                    <input type="text" class="field-name-input input-neumorphic"
                           placeholder="Ej: Estado, Edad..." value="">
                </div>
                ${hintHtml}
            </div>
            <button class="btn-link delete-field" style="color: var(--danger);"
                    onclick="this.parentElement.remove(); checkEmptyState();">
                <i data-lucide="trash-2"></i>
            </button>
        `;


        dropZone.appendChild(fieldCard);
        lucide.createIcons();

        // Focus en el nuevo input automáticamente
        const nameInput = fieldCard.querySelector('.field-name-input');
        const optionsInput = fieldCard.querySelector('.field-options-input');

        setTimeout(() => nameInput.focus(), 50);

        // Inteligencia básica: Si el usuario escribe "Rol" o "Role", sugerir opciones de manager/empleado
        nameInput.addEventListener('input', (e) => {
            const val = e.target.value.toLowerCase().trim();
            if (optionsInput && (val === 'rol' || val === 'role' || val === 'cargo') && !optionsInput.value) {
                optionsInput.value = "Admin, Manager, Empleado";
            }
        });

    }
});

function checkEmptyState() {
    const dropZone = document.getElementById('drop-zone');
    if (dropZone.querySelectorAll('.field-config-card').length === 0) {
        dropZone.innerHTML = `
            <div class="empty-state">
                <i data-lucide="mouse-pointer-2" style="width: 48px; height: 48px; opacity: 0.3;"></i>
                <p>Arrastra aquí tus columnas</p>
            </div>
        `;
        lucide.createIcons();
    }
}

async function saveTable() {
    const name = document.getElementById('table-name').value.trim();
    const description = document.getElementById('table-description').value.trim();
    const fieldCards = document.querySelectorAll('.field-config-card');

    if (!name) {
        showToast("Por favor, ingresa un nombre para la tabla.", "warning");
        return;
    }

    if (fieldCards.length === 0) {
        showToast("La tabla debe tener al menos una columna.", "warning");
        return;
    }

    const fields = [];
    let valid = true;

    fieldCards.forEach(card => {
        const input = card.querySelector('.field-name-input');
        const optInput = card.querySelector('.field-options-input');
        const fieldName = input.value.trim();
        const optionsVal = optInput ? optInput.value.trim() : null;

        if (!fieldName) {
            input.style.borderColor = 'var(--danger)';
            valid = false;
        } else {
            input.style.borderColor = '';
            fields.push({
                name: fieldName,
                field_type: card.dataset.type,
                options: optionsVal || null
            });
        }
    });

    if (!valid) {
        showToast("Por favor, asigna un nombre a todas las columnas.", "warning");
        return;
    }

    const payload = {
        name: name,
        description: description,
        fields: fields
    };

    const btn = document.getElementById('btn-save-table');
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader" class="spin"></i> Guardando...';
    lucide.createIcons();

    try {
        const response = await fetch('/api/tables/full', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            window.appIsDirty = false;
            showToast("¡Tabla creada con éxito!", "success");
            setTimeout(() => {
                window.location.href = '/tables-view';
            }, 1000);
        } else {
            const error = await response.json();
            showToast("Error: " + (error.detail || "No se pudo crear la tabla"), "error");
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="save"></i> Guardar Tabla';
            lucide.createIcons();
        }
    } catch (err) {
        console.error(err);
        showToast("Error de conexión", "error");
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="save"></i> Guardar Tabla';
        lucide.createIcons();
    }
}
