document.addEventListener('DOMContentLoaded', () => {
    const buscador = document.getElementById('buscador-cultivos');
    const tabla = document.getElementById('tabla-cultivos').getElementsByTagName('tbody')[0];
    const filas = tabla.getElementsByTagName('tr');
    const noResult = document.getElementById('no-result-cultivos');

    buscador.addEventListener('input', function() {
        const filtro = this.value.toLowerCase().trim();
        let coincidencias = 0;

        for (let i = 0; i < filas.length; i++) {
            if (filas[i].id === 'no-result-cultivos') continue;

            const celdas = filas[i].getElementsByTagName('td');
            let textoFila = '';
            for (let j = 0; j < celdas.length - 1; j++) { // Excluye columna de Acciones
                textoFila += celdas[j].textContent.toLowerCase() + ' ';
            }

            if (textoFila.includes(filtro)) {
                filas[i].style.display = '';
                coincidencias++;
            } else {
                filas[i].style.display = 'none';
            }
        }

        noResult.style.display = (coincidencias === 0) ? '' : 'none';
    });
});