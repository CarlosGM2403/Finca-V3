// Mostrar alertas de Flask
document.addEventListener('DOMContentLoaded', function() {
    const flashData = document.getElementById('flash-data');
    
    if (flashData) {
        const icon = flashData.dataset.icon;
        const message = flashData.dataset.message;
        
        let iconType = 'info';
        if (icon === 'success') iconType = 'success';
        else if (icon === 'error' || icon === 'danger') iconType = 'error';
        else if (icon === 'warning') iconType = 'warning';
        
        Swal.fire({
            icon: iconType,
            title: iconType === 'success' ? '¡Éxito!' : iconType === 'error' ? 'Error' : 'Información',
            text: message,
            background: '#1e1e1e',
            color: '#fff',
            confirmButtonColor: '#00ff88',
            confirmButtonText: 'Entendido'
        });
    }
});

// Función para ver detalle del empleado (ACTUALIZADA)
function verDetalle(userId, nombre) {
    const modal = document.getElementById('modalDetalle');
    const modalLabel = document.getElementById('modalDetalleLabel');
    const modalContenido = document.getElementById('modalDetalleContenido');
    
    modalLabel.innerHTML = `<i class="fas fa-user-chart"></i> Detalle de ${nombre}`;
    modal.classList.add('active');
    
    // Mostrar spinner de carga
    modalContenido.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Cargando información...</p>
        </div>
    `;
    
    // Cargar datos via AJAX
    fetch(`/detalle_productividad/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let html = '<div class="detalle-grid">';
                
                // ============== ACTIVIDADES ==============
                html += `
                    <div class="detalle-seccion">
                        <h4><i class="fas fa-clipboard-list"></i> Actividades Recientes</h4>
                        <div class="lista-items">
                `;
                
                if (data.actividades.length > 0) {
                    data.actividades.forEach(act => {
                        html += `
                            <div class="item-detalle">
                                <strong>${act.actividad}</strong>
                                <p>${act.insumos || 'Sin insumos especificados'}</p>
                                <small><i class="far fa-calendar"></i> ${act.fecha}</small>
                            </div>
                        `;
                    });
                } else {
                    html += '<div class="sin-items">Sin actividades en este período</div>';
                }
                
                html += '</div></div>';
                
                // ============== PROBLEMAS ==============
                html += `
                    <div class="detalle-seccion">
                        <h4><i class="fas fa-exclamation-triangle"></i> Problemas Reportados</h4>
                        <div class="lista-items">
                `;
                
                if (data.problemas.length > 0) {
                    data.problemas.forEach(prob => {
                        html += `
                            <div class="item-detalle">
                                <strong>${prob.tipo}</strong>
                                <p>${prob.descripcion}</p>
                                <small><i class="far fa-calendar"></i> ${prob.fecha}</small>
                            </div>
                        `;
                    });
                } else {
                    html += '<div class="sin-items">Sin problemas reportados</div>';
                }
                
                html += '</div></div>';
                
                // ============== TRATAMIENTOS ==============
                html += `
                    <div class="detalle-seccion">
                        <h4><i class="fas fa-medkit"></i> Tratamientos Registrados</h4>
                        <div class="lista-items">
                `;
                
                if (data.tratamientos.length > 0) {
                    data.tratamientos.forEach(trat => {
                        html += `
                            <div class="item-detalle">
                                <strong>${trat.cultivo}</strong>
                                <p>${trat.tratamiento}</p>
                                <small><i class="fas fa-flag"></i> Prioridad: ${trat.prioridad} | <i class="far fa-calendar"></i> ${trat.fecha}</small>
                            </div>
                        `;
                    });
                } else {
                    html += '<div class="sin-items">Sin tratamientos registrados</div>';
                }
                
                html += '</div></div>';
                
                // ============== SIEMBRAS (NUEVO) ==============
                html += `
                    <div class="detalle-seccion">
                        <h4><i class="fas fa-seedling"></i> Siembras Realizadas</h4>
                        <div class="lista-items">
                `;
                
                if (data.siembras && data.siembras.length > 0) {
                    data.siembras.forEach(siembra => {
                        html += `
                            <div class="item-detalle">
                                <strong>${siembra.cultivo}</strong>
                                <p>${siembra.detalle}</p>
                                <small><i class="far fa-calendar"></i> ${siembra.fecha}</small>
                            </div>
                        `;
                    });
                } else {
                    html += '<div class="sin-items">Sin siembras registradas</div>';
                }
                
                html += '</div></div>';
                
                html += '</div>'; // Cerrar detalle-grid
                
                modalContenido.innerHTML = html;
            } else {
                modalContenido.innerHTML = `
                    <div class="sin-items" style="padding: 40px;">
                        <i class="fas fa-exclamation-circle" style="font-size: 48px; color: #ff4444; margin-bottom: 15px;"></i>
                        <p>Error al cargar los datos: ${data.error}</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            modalContenido.innerHTML = `
                <div class="sin-items" style="padding: 40px;">
                    <i class="fas fa-exclamation-circle" style="font-size: 48px; color: #ff4444; margin-bottom: 15px;"></i>
                    <p>Error de conexión. Por favor, intenta de nuevo.</p>
                </div>
            `;
            console.error('Error:', error);
        });
}

// Función para cerrar modal
function cerrarModal() {
    const modal = document.getElementById('modalDetalle');
    modal.classList.remove('active');
}

// Cerrar modal al hacer clic fuera
document.getElementById('modalDetalle')?.addEventListener('click', function(e) {
    if (e.target === this) {
        cerrarModal();
    }
});

// Filtros de tabla
document.addEventListener('DOMContentLoaded', function() {
    const buscarInput = document.getElementById('buscarEmpleado');
    const filtroRol = document.getElementById('filtroRol');
    const filas = document.querySelectorAll('.fila-empleado');
    
    function filtrarTabla() {
        const textoBusqueda = buscarInput?.value.toLowerCase() || '';
        const rolSeleccionado = filtroRol?.value || '';
        
        filas.forEach(fila => {
            const empleado = fila.querySelector('.empleado-info strong')?.textContent.toLowerCase() || '';
            const rol = fila.dataset.rol || '';
            
            const coincideTexto = empleado.includes(textoBusqueda);
            const coincideRol = !rolSeleccionado || rol === rolSeleccionado;
            
            if (coincideTexto && coincideRol) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    }
    
    buscarInput?.addEventListener('input', filtrarTabla);
    filtroRol?.addEventListener('change', filtrarTabla);
});