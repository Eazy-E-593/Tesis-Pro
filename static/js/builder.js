document.addEventListener('DOMContentLoaded', () => {
    const draggables = document.querySelectorAll('.draggable-item');
    const dropZone = document.getElementById('drop-zone');
    let fieldCount = 0;
    let draggedData = null;

    // ── Sidebar items: dragstart / dragend / click ───────────────────────────
    draggables.forEach(draggable => {
        draggable.addEventListener('dragstart', (e) => {
            draggedData = {
                type:  draggable.dataset.type,
                label: draggable.querySelector('span').innerText,
                icon:  draggable.querySelector('i').getAttribute('data-lucide')
            };
            e.dataTransfer.setData('text/plain', draggable.dataset.type);
            draggable.classList.add('dragging');
        });

        draggable.addEventListener('dragend', () => {
            draggable.classList.remove('dragging');
            // NO borramos draggedData aquí: en Chrome el drop llega primero,
            // pero en Brave/Firefox puede llegar después. Lo borramos en drop.
        });

        // Click como alternativa táctil / accesible
        draggable.addEventListener('click', () => {
            addFieldToCanvas(
                draggable.dataset.type,
                draggable.querySelector('span').innerText,
                draggable.querySelector('i').getAttribute('data-lucide')
            );
        });
    });

    // ── Document-level dragover ───────────────────────────────────────────────
    // PROBLEMA RAÍZ: cuando ya hay tarjetas dentro del drop-zone, el cursor
    // aterriza en un HIJO (field-config-card), no en el drop-zone en sí.
    // Ese hijo no tiene preventDefault() → el navegador bloquea el drop con 🚫.
    // Solución: capturar en document y comprobar si el target está dentro del zone.
    document.addEventListener('dragover', (e) => {
        if (dropZone.contains(e.target) || e.target === dropZone) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            dropZone.classList.add('drop-zone-active');
        } else {
            dropZone.classList.remove('drop-zone-active');
        }
    });

    document.addEventListener('dragleave', (e) => {
        // Quitar highlight solo cuando abandonamos completamente el drop-zone
        if (e.target === dropZone && !dropZone.contains(e.relatedTarget)) {
            dropZone.classList.remove('drop-zone-active');
        }
    });

    document.addEventListener('drop', (e) => {
        dropZone.classList.remove('drop-zone-active');
        if (dropZone.contains(e.target) || e.target === dropZone) {
            e.preventDefault();
            if (!draggedData) return;
            addFieldToCanvas(draggedData.type, draggedData.label, draggedData.icon);
        }
        draggedData = null;
    });

    // ── Agregar tarjeta al canvas ─────────────────────────────────────────────
    function addFieldToCanvas(type, label, iconName) {
        fieldCount++;

        const emptyState = dropZone.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        const fieldCard = document.createElement('div');
        fieldCard.className = 'field-config-card glass-panel';
        fieldCard.dataset.type = type;
        fieldCard.id = `field-${fieldCount}`;

        fieldCard.innerHTML = `
            <div class="field-drag-handle">
                <i data-lucide="grip-vertical"></i>
            </div>
            <div class="field-info">
                <div class="field-type-badge">
                    <i data-lucide="${iconName}" style="width: 14px;"></i> ${label}
                </div>
                <input type="text" class="field-name-input input-neumorphic"
                       placeholder="Nombre de la columna..." value="">
            </div>
            <button class="btn-link delete-field"
                    onclick="this.parentElement.remove(); checkEmptyState();">
                <i data-lucide="trash-2"></i>
            </button>
        `;

        dropZone.appendChild(fieldCard);
        lucide.createIcons();
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
    const fieldInputs = document.querySelectorAll('.field-name-input');
    const fieldCards = document.querySelectorAll('.field-config-card');

    if (!name) {
        alert("Por favor, ingresa un nombre para la tabla.");
        return;
    }

    if (fieldCards.length === 0) {
        alert("La tabla debe tener al menos una columna.");
        return;
    }

    const fields = [];
    let valid = true;

    fieldCards.forEach(card => {
        const input = card.querySelector('.field-name-input');
        const fieldName = input.value.trim();
        if (!fieldName) {
            input.style.borderColor = 'var(--danger)';
            valid = false;
        } else {
            input.style.borderColor = '';
            fields.push({
                name: fieldName,
                field_type: card.dataset.type
            });
        }
    });

    if (!valid) {
        alert("Por favor, asigna un nombre a todas las columnas.");
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
            alert("¡Tabla creada con éxito!");
            window.location.href = '/tables-view';
        } else {
            const error = await response.json();
            alert("Error: " + (error.detail || "No se pudo crear la tabla"));
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="save"></i> Guardar Tabla';
            lucide.createIcons();
        }
    } catch (err) {
        console.error(err);
        alert("Error de conexión");
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="save"></i> Guardar Tabla';
        lucide.createIcons();
    }
}
