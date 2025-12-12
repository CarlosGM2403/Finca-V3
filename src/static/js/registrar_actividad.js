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

// ==================== CÁMARA ====================
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const preview = document.getElementById("preview");
const tomarFoto = document.getElementById("tomarFoto");
const borrarFoto = document.getElementById("borrarFoto");
const evidenciaInput = document.getElementById("evidenciaInput");

// Iniciar cámara
navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error al acceder a la cámara:", err);
        Swal.fire({
            icon: 'error',
            title: 'Error de Cámara',
            text: 'No se pudo acceder a la cámara. Verifica los permisos.',
            background: '#1e1e1e',
            color: '#fff',
            confirmButtonColor: '#dc3545'
        });
    });

// Tomar foto
tomarFoto.addEventListener("click", () => {
    if (!video.videoWidth || !video.videoHeight) {
        Swal.fire({
            icon: 'warning',
            title: 'Espera un momento',
            text: 'La cámara aún no está lista',
            background: '#1e1e1e',
            color: '#fff',
            confirmButtonColor: '#ffc107'
        });
        return;
    }

    const maxSize = 800;
    const ctx = canvas.getContext("2d");

    let w = video.videoWidth;
    let h = video.videoHeight;

    if (w > h && w > maxSize) {
        h = Math.round((h * maxSize) / w);
        w = maxSize;
    } else if (h >= w && h > maxSize) {
        w = Math.round((w * maxSize) / h);
        h = maxSize;
    }

    canvas.width = w;
    canvas.height = h;
    ctx.drawImage(video, 0, 0, w, h);

    const dataUrl = canvas.toDataURL("image/jpeg", 0.8);

    preview.src = dataUrl;
    preview.style.display = "block";
    video.style.display = "none";

    evidenciaInput.value = dataUrl;

    // Feedback visual
    Swal.fire({
        icon: 'success',
        title: '¡Foto capturada!',
        text: 'Evidencia agregada correctamente',
        background: '#1e1e1e',
        color: '#fff',
        confirmButtonColor: '#00ff88',
        timer: 1500,
        showConfirmButton: false
    });
});

// Borrar foto
borrarFoto.addEventListener("click", () => {
    preview.src = "";
    preview.style.display = "none";
    video.style.display = "block";
    evidenciaInput.value = "";

    Swal.fire({
        icon: 'info',
        title: 'Foto eliminada',
        text: 'Puedes tomar una nueva foto',
        background: '#1e1e1e',
        color: '#fff',
        confirmButtonColor: '#17a2b8',
        timer: 1500,
        showConfirmButton: false
    });
});

// ==================== CONTADOR DE INSUMOS ====================
const insumosSelect = document.getElementById('insumos');
const insumosCount = document.getElementById('insumos-count');

if (insumosSelect && insumosCount) {
    insumosSelect.addEventListener('change', function() {
        const selected = Array.from(this.selectedOptions).length;
        insumosCount.textContent = selected;
        
        if (selected === 0) {
            insumosCount.style.color = '#dc3545';
        } else {
            insumosCount.style.color = '#00ff88';
        }
    });
}

// ==================== CONTADOR DE CARACTERES ====================
const observaciones = document.getElementById('observaciones');
const charCount = document.getElementById('char-count');

if (observaciones && charCount) {
    observaciones.addEventListener('input', function() {
        const length = this.value.length;
        charCount.textContent = length;
        
        if (length > 450) {
            charCount.style.color = '#ffc107';
        } else if (length === 500) {
            charCount.style.color = '#dc3545';
        } else {
            charCount.style.color = '#00ff88';
        }
    });
}

// ==================== VALIDACIÓN ANTES DE ENVIAR ====================
document.querySelector('form').addEventListener('submit', function(e) {
    const cultivo = document.getElementById('cultivo').value;
    const actividad = document.getElementById('actividad').value;
    const insumos = Array.from(insumosSelect.selectedOptions);
    const obs = observaciones.value.trim();
    const evidencia = evidenciaInput.value;
    
    // Validar campos obligatorios
    if (!cultivo || !actividad || insumos.length === 0 || !obs) {
        e.preventDefault();
        
        let mensajeError = 'Por favor completa los siguientes campos:\n\n';
        if (!cultivo) mensajeError += '• Cultivo\n';
        if (!actividad) mensajeError += '• Tipo de Actividad\n';
        if (insumos.length === 0) mensajeError += '• Insumos Utilizados (selecciona al menos uno)\n';
        if (!obs) mensajeError += '• Observaciones\n';
        
        Swal.fire({
            icon: 'warning',
            title: 'Faltan campos obligatorios',
            text: mensajeError,
            background: '#1e1e1e',
            color: '#fff',
            confirmButtonColor: '#ffc107',
            confirmButtonText: 'Entendido'
        });
        return false;
    }
    
    // Validar longitud mínima de observaciones
    if (obs.length < 10) {
        e.preventDefault();
        
        Swal.fire({
            icon: 'warning',
            title: 'Observaciones muy cortas',
            text: 'Las observaciones deben tener al menos 10 caracteres',
            background: '#1e1e1e',
            color: '#fff',
            confirmButtonColor: '#ffc107',
            confirmButtonText: 'Entendido'
        });
        return false;
    }
    
    // Advertencia si no hay evidencia fotográfica
    if (!evidencia) {
        e.preventDefault();
        
        Swal.fire({
            icon: 'question',
            title: 'Sin evidencia fotográfica',
            text: '¿Deseas continuar sin foto? La evidencia aumenta tu puntuación de productividad.',
            background: '#1e1e1e',
            color: '#fff',
            showCancelButton: true,
            confirmButtonColor: '#00ff88',
            cancelButtonColor: '#dc3545',
            confirmButtonText: 'Sí, continuar',
            cancelButtonText: 'Agregar foto'
        }).then((result) => {
            if (result.isConfirmed) {
                // Enviar formulario sin evidencia
                e.target.submit();
            }
        });
        return false;
    }
    
    // Confirmar envío
    e.preventDefault();
    
    Swal.fire({
        icon: 'question',
        title: 'Confirmar registro',
        text: '¿Deseas guardar esta actividad?',
        background: '#1e1e1e',
        color: '#fff',
        showCancelButton: true,
        confirmButtonColor: '#00ff88',
        cancelButtonColor: '#6c757d',
        confirmButtonText: '<i class="fas fa-check"></i> Sí, guardar',
        cancelButtonText: '<i class="fas fa-times"></i> Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            // Mostrar loader mientras se guarda
            Swal.fire({
                title: 'Guardando...',
                text: 'Por favor espera',
                background: '#1e1e1e',
                color: '#fff',
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            
            // Enviar formulario
            e.target.submit();
        }
    });
});

// ==================== ATAJOS DE TECLADO ====================
document.addEventListener('keydown', function(e) {
    // Ctrl + S para guardar
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        document.querySelector('form').requestSubmit();
    }
    
    // Espacio para tomar foto (cuando el foco no está en un textarea)
    if (e.code === 'Space' && document.activeElement.tagName !== 'TEXTAREA') {
        e.preventDefault();
        tomarFoto.click();
    }
    
    // Delete para borrar foto
    if (e.key === 'Delete' && preview.style.display === 'block') {
        e.preventDefault();
        borrarFoto.click();
    }
});

// ==================== MEJORAR EXPERIENCIA CON SELECT MÚLTIPLE ====================
if (insumosSelect) {
    // Agregar clase visual a opciones seleccionadas
    insumosSelect.addEventListener('change', function() {
        Array.from(this.options).forEach(option => {
            if (option.selected) {
                option.style.background = 'rgba(0, 255, 136, 0.2)';
                option.style.color = '#00ff88';
            } else {
                option.style.background = '';
                option.style.color = '';
            }
        });
    });
}

// ==================== AUTO-GUARDADO EN LOCALSTORAGE (BORRADOR) ====================
const BORRADOR_KEY = 'actividad_borrador';

// Cargar borrador al iniciar
window.addEventListener('load', function() {
    try {
        const borrador = localStorage.getItem(BORRADOR_KEY);
        if (borrador) {
            const data = JSON.parse(borrador);
            
            Swal.fire({
                icon: 'info',
                title: 'Borrador encontrado',
                text: '¿Deseas recuperar la actividad que estabas registrando?',
                background: '#1e1e1e',
                color: '#fff',
                showCancelButton: true,
                confirmButtonColor: '#00ff88',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, recuperar',
                cancelButtonText: 'No, empezar nuevo'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Restaurar datos
                    if (data.cultivo) document.getElementById('cultivo').value = data.cultivo;
                    if (data.actividad) document.getElementById('actividad').value = data.actividad;
                    if (data.observaciones) document.getElementById('observaciones').value = data.observaciones;
                    
                    // Trigger evento para actualizar contador
                    if (observaciones) {
                        observaciones.dispatchEvent(new Event('input'));
                    }
                    
                    Swal.fire({
                        icon: 'success',
                        title: 'Borrador recuperado',
                        background: '#1e1e1e',
                        color: '#fff',
                        confirmButtonColor: '#00ff88',
                        timer: 1500,
                        showConfirmButton: false
                    });
                } else {
                    // Limpiar borrador
                    localStorage.removeItem(BORRADOR_KEY);
                }
            });
        }
    } catch (e) {
        console.log('Error al cargar borrador:', e);
    }
});

// Guardar borrador mientras se escribe
let borradorTimeout;
function guardarBorrador() {
    clearTimeout(borradorTimeout);
    borradorTimeout = setTimeout(() => {
        try {
            const datos = {
                cultivo: document.getElementById('cultivo').value,
                actividad: document.getElementById('actividad').value,
                observaciones: document.getElementById('observaciones').value,
                timestamp: new Date().toISOString()
            };
            
            if (datos.cultivo || datos.actividad || datos.observaciones) {
                localStorage.setItem(BORRADOR_KEY, JSON.stringify(datos));
            }
        } catch (e) {
            console.log('Error al guardar borrador:', e);
        }
    }, 2000); // Guardar 2 segundos después de dejar de escribir
}

// Escuchar cambios en el formulario
document.getElementById('cultivo')?.addEventListener('change', guardarBorrador);
document.getElementById('actividad')?.addEventListener('change', guardarBorrador);
document.getElementById('observaciones')?.addEventListener('input', guardarBorrador);

// Limpiar borrador al enviar exitosamente
document.querySelector('form').addEventListener('submit', function() {
    setTimeout(() => {
        localStorage.removeItem(BORRADOR_KEY);
    }, 1000);
});

// ==================== ANIMACIÓN DE ENTRADA ====================
document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.actividad-container');
    if (container) {
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            container.style.transition = 'all 0.5s ease';
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 100);
    }
});

console.log('✅ Sistema de registro de actividades cargado correctamente');