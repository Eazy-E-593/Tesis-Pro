function initStaff() {
    switchStaffTab('active');
    // Cargar las solicitudes pendientes en segundo plano para actualizar el badge de la pestaña
    updatePendingBadgeOnly();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initStaff);
} else {
    initStaff();
}

window.switchStaffTab = function(tabName) {
    document.querySelectorAll('.staff-tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.tab-link').forEach(el => el.classList.remove('active'));
    
    const content = document.getElementById('staff-content-' + tabName);
    if (content) content.style.display = 'block';
    
    const btn = document.getElementById('tab-btn-' + tabName);
    if (btn) btn.classList.add('active');
    
    if (tabName === 'active') loadActiveUsers();
    if (tabName === 'pending') loadPendingUsers();
    if (tabName === 'inactive') loadInactiveUsers();
};

async function updatePendingBadgeOnly() {
    try {
        const res = await fetch(`/api/users/pending?_=${Date.now()}`);
        if (res.ok) {
            const users = await res.json();
            const badge = document.getElementById('staff-badge');
            const pendingBadge = document.getElementById('staff-pending-badge');
            
            if (users.length > 0) {
                if (badge) {
                    badge.innerText = users.length;
                    badge.style.display = 'inline-flex';
                }
                if (pendingBadge) {
                    pendingBadge.innerText = users.length;
                    pendingBadge.style.display = 'inline-block';
                }
            } else {
                if (badge) badge.style.display = 'none';
                if (pendingBadge) pendingBadge.style.display = 'none';
            }
        }
    } catch (e) {
        console.error(e);
    }
}

async function loadPendingUsers() {
    const container = document.getElementById('pending-users-container');
    try {
        const res = await fetch(`/api/users/pending?_=${Date.now()}`);
        if (!res.ok) {
            container.innerHTML = '<p class="text-muted">No se pudieron cargar las solicitudes.</p>';
            return;
        }
        const users = await res.json();
        
        const badge = document.getElementById('staff-badge');
        const pendingBadge = document.getElementById('staff-pending-badge');

        if (users.length === 0) {
            container.innerHTML = '<p class="text-muted" style="font-size: 0.9rem;"><i data-lucide="check-circle" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;"></i> No hay solicitudes pendientes.</p>';
            lucide.createIcons();
            
            if (badge) badge.style.display = 'none';
            if (pendingBadge) pendingBadge.style.display = 'none';
            return;
        }

        if (badge) {
            badge.innerText = users.length;
            badge.style.display = 'inline-flex';
        }
        if (pendingBadge) {
            pendingBadge.innerText = users.length;
            pendingBadge.style.display = 'inline-block';
        }

        let html = '<div style="display: flex; flex-direction: column; gap: 12px;">';
        users.forEach(u => {
            html += `
                <div class="glass-panel" style="padding: 16px; display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2); border-radius: var(--radius-md); overflow: hidden;">
                    <div>
                        <strong style="display: block; font-size: 1.1rem; color: var(--text-main);">${u.full_name}</strong>
                        <span style="font-size: 0.85rem; color: var(--text-muted);">${u.email} | CI/RUC: ${u.cedula}</span>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <select id="role-select-${u.id}" class="input-neumorphic" style="padding: 8px 12px; font-size: 0.9rem; height: auto; min-width: 130px; background: var(--secondary);">
                            <option value="empleado">Empleado</option>
                            <option value="manager">Manager</option>
                        </select>
                        <button class="btn btn-primary" onclick="approveUser(${u.id}, this)">Aprobar</button>
                        <button class="btn btn-secondary" style="background: var(--danger); border-color: var(--danger); color: white;" onclick="rejectUser(${u.id}, this, true)">Rechazar</button>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;
        lucide.createIcons();
    } catch (e) {
        console.error(e);
        container.innerHTML = '<p class="text-muted">Error de conexión.</p>';
    }
}

async function loadActiveUsers() {
    const container = document.getElementById('active-users-container');
    try {
        const res = await fetch(`/api/users/active?_=${Date.now()}`);
        if (!res.ok) {
            container.innerHTML = '<p class="text-muted">No se pudo cargar el personal activo.</p>';
            return;
        }
        const users = await res.json();
        
        if (users.length === 0) {
            container.innerHTML = '<p class="text-muted" style="font-size: 0.9rem;">No hay personal activo aún.</p>';
            return;
        }

        let html = `
            <table class="data-table" style="width: 100%;">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Nombre</th>
                        <th>Email</th>
                        <th>Rol</th>
                        <th style="text-align: center; width: 80px;">Acción</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        users.forEach(u => {
            let btnRechazar = u.role === 'admin' ? '' : `<button class="btn-link" style="color: var(--danger); padding: 4px; border: none; background: transparent; cursor: pointer;" onclick="rejectUser(${u.id}, this, false)" title="Dar de Baja (Despedir)"><i data-lucide="trash-2" style="width: 18px; height: 18px;"></i></button>`;
            
            html += `
                <tr>
                    <td style="font-family: monospace; color: var(--primary);">${u.employee_code || '-'}</td>
                    <td>${u.full_name}</td>
                    <td>${u.email}</td>
                    <td style="text-transform: capitalize;">${u.role}</td>
                    <td style="text-align: center;">${btnRechazar}</td>
                </tr>
            `;
        });
        html += '</tbody></table>';
        container.innerHTML = html;
        lucide.createIcons();
    } catch (e) {
        console.error(e);
        container.innerHTML = '<p class="text-muted">Error de conexión.</p>';
    }
}

async function loadInactiveUsers() {
    const container = document.getElementById('inactive-users-container');
    try {
        const res = await fetch(`/api/users/inactive?_=${Date.now()}`);
        if (!res.ok) {
            container.innerHTML = '<p class="text-muted">No se pudo cargar el historial de bajas.</p>';
            return;
        }
        const users = await res.json();
        
        if (users.length === 0) {
            container.innerHTML = '<p class="text-muted" style="font-size: 0.9rem;"><i data-lucide="archive" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;"></i> No hay empleados en el historial de bajas.</p>';
            lucide.createIcons();
            return;
        }

        let html = `
            <table class="data-table" style="width: 100%;">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Nombre</th>
                        <th>Email</th>
                        <th>Rol Original</th>
                        <th style="text-align: center; width: 180px;">Acciones</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        users.forEach(u => {
            html += `
                <tr style="opacity: 0.75;">
                    <td style="font-family: monospace; color: var(--text-muted);">${u.employee_code || '-'}</td>
                    <td>${u.full_name} <span class="badge" style="background: rgba(239, 68, 68, 0.12); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); font-size: 0.7rem; padding: 2px 6px; margin-left: 6px;">Baja</span></td>
                    <td>${u.email}</td>
                    <td style="text-transform: capitalize;">${u.role}</td>
                    <td style="text-align: center;">
                        <div style="display: flex; gap: 8px; justify-content: center; align-items: center;">
                            <a href="/audits-view?q=${u.employee_code}" class="btn btn-secondary" style="padding: 4px 8px; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px; text-decoration: none;" title="Ver Historial de Auditoría">
                                <i data-lucide="search" style="width: 14px; height: 14px;"></i> Auditar
                            </a>
                            <button class="btn btn-primary" onclick="rehireUser(${u.id}, this)" style="padding: 4px 8px; font-size: 0.75rem; background: var(--success); border: none; display: inline-flex; align-items: center; gap: 4px;" title="Reactivar y Recontratar">
                                <i data-lucide="refresh-cw" style="width: 14px; height: 14px;"></i> Reactivar
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        html += '</tbody></table>';
        container.innerHTML = html;
        lucide.createIcons();
    } catch (e) {
        console.error(e);
        container.innerHTML = '<p class="text-muted">Error de conexión.</p>';
    }
}

async function approveUser(id, btn) {
    const role = document.getElementById(`role-select-${id}`).value;
    const originalContent = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader" class="spin" style="width:16px;"></i>...';
    btn.disabled = true;
    lucide.createIcons();

    try {
        const res = await fetch(`/api/users/${id}/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: role })
        });
        const data = await res.json();
        
        if (res.ok) {
            if (data.email_error) {
                showToast("Usuario aprobado, pero falló el envío del correo de aviso.", "warning");
            } else {
                showToast("Usuario aprobado y notificado por correo.", "success");
            }
            await loadPendingUsers();
        } else {
            showToast("Error al aprobar usuario.", "error");
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    } catch (e) {
        console.error(e);
        showToast("Error de conexión.", "error");
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
}

async function rejectUser(id, btn, isPending = false) {
    const confirmMsg = isPending 
        ? "¿Seguro que deseas rechazar la solicitud de este usuario?"
        : "¿Seguro que deseas dar de baja (despedir) a este empleado?";
        
    let ok = confirm(confirmMsg);
    if (!ok) return;
    
    const originalContent = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader" class="spin" style="width:16px;"></i>';
    btn.disabled = true;
    lucide.createIcons();
    
    try {
        const res = await fetch(`/api/users/${id}/reject`, { method: 'POST' });
        const data = await res.json();
        
        if (res.ok) {
            if (isPending) {
                showToast("Solicitud rechazada con éxito.", "info");
                await loadPendingUsers();
            } else {
                if (data.email_error) {
                    showToast("Empleado dado de baja, pero falló el envío de correo de aviso.", "warning");
                } else {
                    showToast("Empleado dado de baja con éxito y notificado por correo.", "success");
                }
                await loadActiveUsers();
            }
        } else {
            showToast("Error al procesar la acción.", "error");
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    } catch (e) {
        console.error(e);
        showToast("Error de conexión.", "error");
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
}

async function rehireUser(id, btn) {
    let ok = confirm("¿Seguro que deseas reactivar y recontratar a este empleado?");
    if (!ok) return;
    
    const originalContent = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader" class="spin" style="width:16px;"></i>';
    btn.disabled = true;
    lucide.createIcons();
    
    try {
        const res = await fetch(`/api/users/${id}/rehire`, { method: 'POST' });
        const data = await res.json();
        
        if (res.ok) {
            if (data.email_error) {
                showToast("Empleado reactivado, pero falló el envío del correo de aviso.", "warning");
            } else {
                showToast("Empleado reactivado con éxito y notificado por correo.", "success");
            }
            await loadInactiveUsers();
        } else {
            showToast("Error al reactivar al empleado.", "error");
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    } catch (e) {
        console.error(e);
        showToast("Error de conexión.", "error");
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
}
