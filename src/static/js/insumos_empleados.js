// ==================== ALERTAS SWEETALERT ====================
const flashData = document.getElementById('flash-data');
if (flashData) {
    const icon = flashData.getAttribute('data-icon');
    const message = flashData.getAttribute('data-message');
    Swal.fire({
        icon: icon,
        title: icon === 'success' ? '¡Éxito!' : 'Error',
        text: message,
        confirmButtonColor: '#00ff88',
        timer: 3000,
        timerProgressBar: true
    });
}

// ==================== BUSCADOR EN TIEMPO REAL ====================
const buscador = document.getElementById('buscador-insumos');
const tabla = document.getElementById('tabla-insumos');
const noResult = document.getElementById('no-result');

if (buscador && tabla) {
    const filas = tabla.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    buscador.addEventListener('input', function() {
        const filtro = this.value.toLowerCase();
        let hayResultados = false;

        for (let i = 0; i < filas.length; i++) {
            const fila = filas[i];
            const texto = fila.textContent.toLowerCase();
            
            if (texto.includes(filtro)) {
                fila.style.display = '';
                hayResultados = true;
            } else {
                fila.style.display = 'none';
            }
        }

        // Mostrar mensaje si no hay resultados
        if (filas.length > 0 && !filas[0].querySelector('.sin-datos')) {
            tabla.style.display = hayResultados ? '' : 'none';
            noResult.style.display = hayResultados ? 'none' : 'block';
        }
    });
}