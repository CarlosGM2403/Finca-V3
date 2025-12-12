// ==================== INICIALIZACIÓN ==================== 
document.addEventListener('DOMContentLoaded', function() {
    inicializarBuscador();
    inicializarObservaciones();
    inicializarModalEventos();
    cargarFiltrosReporte();
    mostrarFlashMessages();
    inicializarFechasPorDefecto();
});

// ==================== FLASH MESSAGES CON SWEETALERT2 ==================== 
function mostrarFlashMessages() {
    const flashData = document.getElementById('flash-data');
    
    if (flashData) {
        const icon = flashData.dataset.icon;
        const message = flashData.dataset.message;
        
        let iconType = 'info';
        let title = 'Información';
        
        if (icon === 'success') {
            iconType = 'success';
            title = '¡Éxito!';
        } else if (icon === 'error' || icon === 'danger') {
            iconType = 'error';
            title = 'Error';
        } else if (icon === 'warning') {
            iconType = 'warning';
            title = 'Advertencia';
        }
        
        Swal.fire({
            icon: iconType,
            title: title,
            text: message,
            background: '#1e1e1e',
            color: '#fff',
            confirmButtonColor: '#4db856',
            confirmButtonText: 'Entendido',
            showClass: {
                popup: 'animate__animated animate__fadeInDown'
            },
            hideClass: {
                popup: 'animate__animated animate__fadeOutUp'
            }
        });
    }
}

// ==================== BUSCADOR DE TRATAMIENTOS ==================== 
function inicializarBuscador() {
    const buscador = document.getElementById('buscador-tratamientos');
    const filas = document.querySelectorAll('#tabla-tratamientos tbody tr');
    const mensaje = document.getElementById('no-result-siembra');

    if (!buscador || !filas.length) return;

    buscador.addEventListener('input', function() {
        const texto = this.value.toLowerCase().trim();
        let algunaVisible = false;

        filas.forEach(fila => {
            const contenido = fila.textContent.toLowerCase();
            const coincide = contenido.includes(texto);
            
            fila.style.display = coincide ? '' : 'none';
            
            if (coincide) {
                algunaVisible = true;
            }
        });

        if (mensaje) {
            mensaje.style.display = algunaVisible ? 'none' : 'block';
        }
    });
}

// ==================== SISTEMA DE OBSERVACIONES ==================== 
let idTratamientoActual = null;

function inicializarObservaciones() {
    const botonesObservaciones = document.querySelectorAll('.btn-observaciones');
    
    botonesObservaciones.forEach(btn => {
        btn.addEventListener('click', function() {
            const idTratamiento = this.getAttribute('data-id-tratamiento');
            verObservaciones(idTratamiento);
        });
    });
    
    // Contador de caracteres en tiempo real
    const textareaObservacion = document.getElementById('nueva-observacion');
    const contadorCaracteres = document.getElementById('contador');

    if (textareaObservacion && contadorCaracteres) {
        textareaObservacion.addEventListener('input', function() {
            const longitud = this.value.length;
            contadorCaracteres.textContent = longitud;
            
            if (longitud >= 5) {
                contadorCaracteres.style.color = '#4db856';
                contadorCaracteres.classList.add('valido');
            } else {
                contadorCaracteres.style.color = '#dc3545';
                contadorCaracteres.classList.remove('valido');
            }
        });
    }

    // Enviar observación
    const formObservacion = document.getElementById('form-observacion');
    if (formObservacion) {
        formObservacion.addEventListener('submit', function(e) {
            e.preventDefault();
            enviarObservacion();
        });
    }
}

function verObservaciones(idTratamiento) {
    idTratamientoActual = idTratamiento;
    
    // Establecer ID en campos ocultos
    const modalInput = document.getElementById('id_tratamiento_modal');
    const formInput = document.getElementById('id_tratamiento_form');
    
    if (modalInput) modalInput.value = idTratamiento;
    if (formInput) formInput.value = idTratamiento;
    
    // Abrir modal
    const modal = document.getElementById('modal-observaciones');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
    
    // Cargar observaciones
    cargarObservaciones(idTratamiento);
}

function cargarObservaciones(idTratamiento) {
    const listaObservaciones = document.getElementById('lista-observaciones');
    
    if (!listaObservaciones) return;
    
    // Mostrar loading
    listaObservaciones.innerHTML = `
        <div class="loading-observaciones">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Cargando observaciones...</p>
        </div>
    `;
    
    // Hacer petición AJAX
    fetch(`/obtener_observaciones/${idTratamiento}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                mostrarObservaciones(data.observaciones);
            } else {
                mostrarErrorObservaciones('Error al cargar observaciones');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarErrorObservaciones('Error de conexión. Por favor, intenta de nuevo.');
        });
}

function mostrarObservaciones(observaciones) {
    const listaObservaciones = document.getElementById('lista-observaciones');
    
    if (!listaObservaciones) return;
    
    if (observaciones.length === 0) {
        listaObservaciones.innerHTML = `
            <div class="sin-observaciones">
                <i class="fas fa-inbox" style="font-size: 48px; color: #444; margin-bottom: 15px;"></i>
                <p>No hay observaciones registradas aún.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    observaciones.forEach(obs => {
        html += `
            <div class="observacion-item">
                <div class="observacion-header">
                    <span class="observacion-usuario">
                        <i class="fa-solid fa-user"></i> ${escapeHtml(obs.usuario)}
                    </span>
                    <span class="observacion-fecha">
                        <i class="fa-solid fa-clock"></i> ${escapeHtml(obs.fecha)}
                    </span>
                </div>
                <div class="observacion-texto">${escapeHtml(obs.observacion)}</div>
            </div>
        `;
    });
    
    listaObservaciones.innerHTML = html;
}

function mostrarErrorObservaciones(mensaje) {
    const listaObservaciones = document.getElementById('lista-observaciones');
    
    if (!listaObservaciones) return;
    
    listaObservaciones.innerHTML = `
        <div class="error-observaciones">
            <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #dc3545; margin-bottom: 15px;"></i>
            <p>${escapeHtml(mensaje)}</p>
        </div>
    `;
}

function enviarObservacion() {
    const textarea = document.getElementById('nueva-observacion');
    const observacion = textarea.value.trim();
    
    // Validar longitud mínima
    if (observacion.length < 5) {
        Swal.fire({
            icon: 'warning',
            title: 'Observación muy corta',
            text: 'La observación debe tener al menos 5 caracteres',
            background: '#1e1e1e',
            color: '#fff',
            confirmButtonColor: '#4db856'
        });
        return;
    }
    
    // Preparar datos del formulario
    const formData = new FormData();
    formData.append('id_tratamiento', idTratamientoActual);
    formData.append('observacion', observacion);
    
    // Mostrar loading
    Swal.fire({
        title: 'Guardando...',
        html: 'Por favor espera',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Enviar petición
    fetch('/agregar_observacion', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                icon: 'success',
                title: '¡Observación agregada!',
                text: 'La observación se guardó correctamente',
                background: '#1e1e1e',
                color: '#fff',
                confirmButtonColor: '#4db856',
                timer: 2000
            });
            
            // Limpiar textarea
            textarea.value = '';
            document.getElementById('contador').textContent = '0';
            document.getElementById('contador').style.color = '#dc3545';
            
            // Recargar observaciones
            cargarObservaciones(idTratamientoActual);
            
            // Actualizar contador en la tabla
            actualizarContadorTabla(idTratamientoActual);
            
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'No se pudo guardar la observación',
                background: '#1e1e1e',
                color: '#fff',
                confirmButtonColor: '#dc3545'
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error de conexión',
            text: 'No se pudo conectar con el servidor',
            background: '#1e1e1e',
            color: '#fff',
            confirmButtonColor: '#dc3545'
        });
    });
}

function actualizarContadorTabla(idTratamiento) {
    const fila = document.querySelector(`tr[data-id-tratamiento="${idTratamiento}"]`);
    if (fila) {
        const badge = fila.querySelector('.badge-observaciones, .badge-observaciones-cero');
        if (badge) {
            let count = parseInt(badge.textContent) || 0;
            count++;
            badge.textContent = count;
            
            // Cambiar clase si era cero
            if (badge.classList.contains('badge-observaciones-cero')) {
                badge.classList.remove('badge-observaciones-cero');
                badge.classList.add('badge-observaciones');
            }
        }
    }
}

// ==================== MODAL - EVENTOS ==================== 
function inicializarModalEventos() {
    const modalObservaciones = document.getElementById('modal-observaciones');
    
    if (modalObservaciones) {
        // Cerrar al hacer clic fuera del contenido
        modalObservaciones.addEventListener('click', function(e) {
            if (e.target === this) {
                cerrarModal();
            }
        });
        
        // Cerrar con tecla ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modalObservaciones.style.display === 'flex') {
                cerrarModal();
            }
        });
    }
}

function cerrarModal() {
    const modal = document.getElementById('modal-observaciones');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    // Limpiar textarea si existe
    const textarea = document.getElementById('nueva-observacion');
    if (textarea) {
        textarea.value = '';
        const contador = document.getElementById('contador');
        if (contador) {
            contador.textContent = '0';
            contador.style.color = '#dc3545';
            contador.classList.remove('valido');
        }
    }
}

// ==================== PANEL DE REPORTE ==================== 
function togglePanel() {
    const panelBody = document.getElementById('panelReporte');
    const btnToggle = document.querySelector('.btn-toggle-panel i');
    
    if (panelBody && btnToggle) {
        panelBody.classList.toggle('oculto');
        
        if (panelBody.classList.contains('oculto')) {
            btnToggle.style.transform = 'rotate(0deg)';
        } else {
            btnToggle.style.transform = 'rotate(180deg)';
        }
    }
}

function limpiarFiltros() {
    // Limpiar inputs de fecha
    const fechaInicio = document.getElementById('fecha_inicio');
    const fechaFin = document.getElementById('fecha_fin');
    
    if (fechaInicio) fechaInicio.value = '';
    if (fechaFin) fechaFin.value = '';
    
    // Limpiar selects
    const cultivoFiltro = document.getElementById('cultivo_filtro');
    const prioridadFiltro = document.getElementById('prioridad_filtro');
    const problemaFiltro = document.getElementById('problema_filtro');
    
    if (cultivoFiltro) cultivoFiltro.value = '';
    if (prioridadFiltro) prioridadFiltro.value = '';
    if (problemaFiltro) problemaFiltro.value = '';
    
    // Feedback visual
    Swal.fire({
        icon: 'info',
        title: 'Filtros limpiados',
        text: 'Todos los filtros han sido restablecidos',
        background: '#1e1e1e',
        color: '#fff',
        confirmButtonColor: '#4db856',
        timer: 1500,
        showConfirmButton: false
    });
}

function cargarFiltrosReporte() {
    const cultivoSelect = document.getElementById('cultivo_filtro');
    
    if (!cultivoSelect) return;
    
    // Hacer petición AJAX para obtener filtros
    fetch('/obtener_filtros_tratamientos')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Llenar select de cultivos
                if (data.cultivos && data.cultivos.length > 0) {
                    data.cultivos.forEach(cultivo => {
                        const option = document.createElement('option');
                        option.value = cultivo;
                        option.textContent = cultivo;
                        cultivoSelect.appendChild(option);
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error al cargar filtros:', error);
        });
}

function inicializarFechasPorDefecto() {
    const fechaInicio = document.getElementById('fecha_inicio');
    const fechaFin = document.getElementById('fecha_fin');
    
    if (!fechaInicio || !fechaFin) return;
    
    // Establecer fecha fin como hoy
    const hoy = new Date();
    fechaFin.value = formatearFecha(hoy);
    
    // Establecer fecha inicio como hace 30 días
    const hace30Dias = new Date();
    hace30Dias.setDate(hace30Dias.getDate() - 30);
    fechaInicio.value = formatearFecha(hace30Dias);
}

function formatearFecha(fecha) {
    const año = fecha.getFullYear();
    const mes = String(fecha.getMonth() + 1).padStart(2, '0');
    const dia = String(fecha.getDate()).padStart(2, '0');
    return `${año}-${mes}-${dia}`;
}

// ==================== UTILIDADES ==================== 
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ==================== VALIDACIÓN DE FORMULARIO DE REPORTE ==================== 
const formReporte = document.querySelector('.form-reporte');
if (formReporte) {
    formReporte.addEventListener('submit', function(e) {
        const fechaInicio = document.getElementById('fecha_inicio').value;
        const fechaFin = document.getElementById('fecha_fin').value;
        
        // Validar que fecha inicio no sea mayor a fecha fin
        if (fechaInicio && fechaFin && fechaInicio > fechaFin) {
            e.preventDefault();
            Swal.fire({
                icon: 'error',
                title: 'Error en fechas',
                text: 'La fecha de inicio no puede ser mayor a la fecha fin',
                background: '#1e1e1e',
                color: '#fff',
                confirmButtonColor: '#dc3545'
            });
            return false;
        }
        
        // Mostrar loading mientras se genera el PDF
        Swal.fire({
            title: 'Generando reporte...',
            html: 'Por favor espera mientras se crea el PDF',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        // Cerrar el loading después de 2 segundos (el PDF se descargará)
        setTimeout(() => {
            Swal.close();
        }, 2000);
    });
}

// ==================== ANIMACIONES AL SCROLL ==================== 
window.addEventListener('scroll', function() {
    const cards = document.querySelectorAll('.stat-card');
    
    cards.forEach(card => {
        const cardPosition = card.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (cardPosition < screenPosition) {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }
    });
});

// Inicializar animación de cards
document.querySelectorAll('.stat-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'all 0.6s ease';
});

// ==================== TOOLTIP PARA BOTONES ==================== 
function inicializarTooltips() {
    const botones = document.querySelectorAll('[title]');
    
    botones.forEach(boton => {
        boton.addEventListener('mouseenter', function() {
            const title = this.getAttribute('title');
            if (title) {
                const tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = title;
                tooltip.style.cssText = `
                    position: absolute;
                    background: rgba(0,0,0,0.9);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    z-index: 10000;
                    pointer-events: none;
                    white-space: nowrap;
                `;
                
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                
                this.tooltipElement = tooltip;
            }
        });
        
        boton.addEventListener('mouseleave', function() {
            if (this.tooltipElement) {
                this.tooltipElement.remove();
                this.tooltipElement = null;
            }
        });
    });
}

// Inicializar tooltips al cargar
document.addEventListener('DOMContentLoaded', inicializarTooltips);

console.log('✅ Sistema de tratamientos cargado correctamente');