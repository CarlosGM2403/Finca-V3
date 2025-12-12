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
            confirmButtonColor: '#dc3545',
            confirmButtonText: 'Entendido'
        });
    }

    // Cargar filtros dinámicamente
    cargarFiltros();

    // Establecer fecha máxima como hoy
    const hoy = new Date().toISOString().split('T')[0];
    const fechaInicio = document.getElementById('fecha_inicio');
    const fechaFin = document.getElementById('fecha_fin');
    
    if (fechaInicio && fechaFin) {
        fechaInicio.max = hoy;
        fechaFin.max = hoy;
        
        // Establecer valores por defecto (últimos 30 días)
        const hace30Dias = new Date();
        hace30Dias.setDate(hace30Dias.getDate() - 30);
        fechaInicio.value = hace30Dias.toISOString().split('T')[0];
        fechaFin.value = hoy;
    }
});

// Función para cargar filtros dinámicamente
async function cargarFiltros() {
    try {
        const response = await fetch('/obtener_filtros_problemas');
        const data = await response.json();
        
        if (data.success) {
            // Llenar filtro de tipos en la página principal
            const filtroTipo = document.getElementById('filtro-tipo');
            if (filtroTipo) {
                data.tipos.forEach(tipo => {
                    const option = document.createElement('option');
                    option.value = tipo;
                    option.textContent = tipo;
                    filtroTipo.appendChild(option);
                });
            }

            // Llenar filtro de tipos en el modal
            const tipoFiltroModal = document.getElementById('tipo_filtro');
            if (tipoFiltroModal) {
                data.tipos.forEach(tipo => {
                    const option = document.createElement('option');
                    option.value = tipo;
                    option.textContent = tipo;
                    tipoFiltroModal.appendChild(option);
                });
            }

            // Llenar filtro de usuarios en el modal
            const usuarioFiltroModal = document.getElementById('usuario_filtro');
            if (usuarioFiltroModal) {
                data.usuarios.forEach(usuario => {
                    const option = document.createElement('option');
                    option.value = usuario.id;
                    option.textContent = usuario.nombre;
                    usuarioFiltroModal.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error al cargar filtros:', error);
    }
}

// Buscador de problemas
const buscador = document.getElementById('buscador-problemas');
const problemaCards = document.querySelectorAll('.problema-card');
const noResult = document.getElementById('no-result-problemas');

if (buscador) {
    buscador.addEventListener('input', function() {
        const filtro = this.value.toLowerCase().trim();
        let coincidencias = 0;

        problemaCards.forEach(card => {
            const texto = card.textContent.toLowerCase();
            const coincide = texto.includes(filtro);

            if (coincide) {
                card.style.display = 'block';
                coincidencias++;
            } else {
                card.style.display = 'none';
            }
        });

        if (noResult) {
            noResult.style.display = (coincidencias === 0) ? 'block' : 'none';
        }
    });
}

// Filtro por tipo
const filtroTipo = document.getElementById('filtro-tipo');
if (filtroTipo) {
    filtroTipo.addEventListener('change', function() {
        const tipoSeleccionado = this.value.toLowerCase();
        let coincidencias = 0;

        problemaCards.forEach(card => {
            const tipo = card.dataset.tipo.toLowerCase();
            const textoBuscador = buscador ? buscador.value.toLowerCase() : '';
            
            const coincideTipo = !tipoSeleccionado || tipo === tipoSeleccionado;
            const coincideBuscador = !textoBuscador || card.textContent.toLowerCase().includes(textoBuscador);

            if (coincideTipo && coincideBuscador) {
                card.style.display = 'block';
                coincidencias++;
            } else {
                card.style.display = 'none';
            }
        });

        if (noResult) {
            noResult.style.display = (coincidencias === 0) ? 'block' : 'none';
        }
    });
}

// Funciones del modal de reporte
function mostrarModalReporte() {
    const modal = document.getElementById('modalReporte');
    if (modal) {
        modal.classList.add('active');
    }
}

function cerrarModalReporte() {
    const modal = document.getElementById('modalReporte');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Cerrar modal al hacer clic fuera
document.getElementById('modalReporte')?.addEventListener('click', function(e) {
    if (e.target === this) {
        cerrarModalReporte();
    }
});

// Modal para ver imagen ampliada
problemaCards.forEach(card => {
    const imagen = card.querySelector('.problema-imagen img');
    if (imagen) {
        imagen.addEventListener('click', function(e) {
            e.stopPropagation();
            mostrarImagenAmpliada(this.src);
        });
    }
});

function mostrarImagenAmpliada(src) {
    const modal = document.getElementById('modalImagen');
    const imagenAmpliada = document.getElementById('imagenAmpliada');
    
    if (modal && imagenAmpliada) {
        imagenAmpliada.src = src;
        modal.classList.add('active');
    }
}

function cerrarModalImagen() {
    const modal = document.getElementById('modalImagen');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Cerrar modal de imagen al hacer clic fuera
document.getElementById('modalImagen')?.addEventListener('click', function(e) {
    if (e.target === this) {
        cerrarModalImagen();
    }
});