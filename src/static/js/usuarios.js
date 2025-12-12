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

// Elementos del DOM
const buscador = document.getElementById('buscador');
const filtroRol = document.getElementById('filtro-rol');
const filtroEstado = document.getElementById('filtro-estado');
const tabla = document.getElementById('tabla-usuarios').getElementsByTagName('tbody')[0];
const filas = Array.from(tabla.getElementsByTagName('tr')).filter(fila => 
    fila.id !== 'no-result' && fila.id !== 'sin-usuarios'
);
const noResult = document.getElementById('no-result');
const totalVisible = document.getElementById('total-visible');
const totalUsuarios = document.getElementById('total-usuarios');

// Función para filtrar la tabla
function filtrarTabla() {
    const textoBusqueda = buscador.value.toLowerCase().trim();
    const rolSeleccionado = filtroRol.value.toLowerCase();
    const estadoSeleccionado = filtroEstado.value.toLowerCase();
    
    let coincidencias = 0;

    filas.forEach(fila => {
        const rol = fila.dataset.rol;
        const estado = fila.dataset.estado;
        const textoFila = fila.textContent.toLowerCase();
        
        const coincideTexto = !textoBusqueda || textoFila.includes(textoBusqueda);
        const coincideRol = !rolSeleccionado || rol === rolSeleccionado;
        const coincideEstado = !estadoSeleccionado || estado === estadoSeleccionado;
        
        if (coincideTexto && coincideRol && coincideEstado) {
            fila.style.display = '';
            coincidencias++;
        } else {
            fila.style.display = 'none';
        }
    });

    // Actualizar contador
    if (totalVisible) {
        totalVisible.textContent = coincidencias;
    }

    // Mostrar/ocultar mensaje de sin resultados
    if (noResult) {
        noResult.style.display = (coincidencias === 0) ? '' : 'none';
    }
}

// Event listeners
if (buscador) {
    buscador.addEventListener('input', filtrarTabla);
}

if (filtroRol) {
    filtroRol.addEventListener('change', filtrarTabla);
}

if (filtroEstado) {
    filtroEstado.addEventListener('change', filtrarTabla);
}

// Animación de entrada para las filas
filas.forEach((fila, index) => {
    fila.style.animation = `fadeInUp 0.3s ease ${index * 0.05}s both`;
});

// Agregar estilos de animación si no existen
if (!document.getElementById('custom-animations')) {
    const style = document.createElement('style');
    style.id = 'custom-animations';
    style.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}