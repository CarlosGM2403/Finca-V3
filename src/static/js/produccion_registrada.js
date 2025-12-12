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

// Funciones para el modal
function mostrarModalReporte() {
    const modal = document.getElementById('modalReporte');
    modal.classList.add('active');
    
    // Establecer fecha de hoy como máximo
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('fecha_inicio').setAttribute('max', hoy);
    document.getElementById('fecha_fin').setAttribute('max', hoy);
    
    // Establecer fechas por defecto (últimos 30 días)
    const fechaFin = new Date();
    const fechaInicio = new Date();
    fechaInicio.setDate(fechaInicio.getDate() - 30);
    
    document.getElementById('fecha_fin').value = fechaFin.toISOString().split('T')[0];
    document.getElementById('fecha_inicio').value = fechaInicio.toISOString().split('T')[0];
}

function cerrarModalReporte() {
    const modal = document.getElementById('modalReporte');
    modal.classList.remove('active');
}

// Cerrar modal al hacer clic fuera
document.getElementById('modalReporte')?.addEventListener('click', function(e) {
    if (e.target === this) {
        cerrarModalReporte();
    }
});

// Validar que fecha_fin sea mayor o igual a fecha_inicio
document.getElementById('fecha_fin')?.addEventListener('change', function() {
    const fechaInicio = document.getElementById('fecha_inicio').value;
    const fechaFin = this.value;
    
    if (fechaInicio && fechaFin && fechaFin < fechaInicio) {
        Swal.fire({
            icon: 'warning',
            title: 'Fechas inválidas',
            text: 'La fecha de fin debe ser posterior a la fecha de inicio',
            background: '#1e1e1e',
            color: '#fff',
            confirmButtonColor: '#00ff88'
        });
        this.value = '';
    }
});

// Buscador y filtro combinados
document.addEventListener('DOMContentLoaded', function() {
    const buscador = document.getElementById('buscador-produccion');
    const filtroUsuario = document.getElementById('filtro-usuario');
    const filas = document.querySelectorAll('#tabla-produccion tbody tr');
    const noProduccion = document.getElementById('no-produccion');
    const noResult = document.getElementById('no-result-produccion');

    function filtrarTabla() {
        const busqueda = buscador?.value.toLowerCase() || '';
        const usuarioSeleccionado = filtroUsuario?.value || '';
        let hayResultados = false;

        filas.forEach(fila => {
            // Ignorar las filas de mensajes
            if (fila.id === 'no-produccion' || fila.id === 'no-result-produccion') {
                return;
            }

            const texto = fila.textContent.toLowerCase();
            const empleado = fila.dataset.empleado || '';
            
            const coincideBusqueda = texto.includes(busqueda);
            const coincideUsuario = !usuarioSeleccionado || empleado === usuarioSeleccionado;
            
            if (coincideBusqueda && coincideUsuario) {
                fila.style.display = '';
                hayResultados = true;
            } else {
                fila.style.display = 'none';
            }
        });

        // Ocultar mensaje de "No hay producción"
        if (noProduccion) noProduccion.style.display = 'none';
        
        // Mostrar mensaje si no hay resultados
        if (!hayResultados && (busqueda.length > 0 || usuarioSeleccionado)) {
            noResult.style.display = '';
        } else {
            noResult.style.display = 'none';
        }
    }

    buscador?.addEventListener('input', filtrarTabla);
    filtroUsuario?.addEventListener('change', filtrarTabla);
});