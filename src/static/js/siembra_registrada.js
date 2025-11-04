document.addEventListener('DOMContentLoaded', () => {
    const buscador = document.getElementById('buscador-siembra');
    const tabla = document.getElementById('tabla-siembra').getElementsByTagName('tbody')[0];
    const filas = tabla.getElementsByTagName('tr');
    const noResult = document.getElementById('no-result-siembra');

    buscador.addEventListener('input', function() {
        const filtro = this.value.toLowerCase().trim();
        let coincidencias = 0;

        for (let i = 0; i < filas.length; i++) {
            if (filas[i].id === 'no-result-siembra') continue;

            const celdas = filas[i].getElementsByTagName('td');
            let textoFila = '';
            for (let j = 0; j < celdas.length; j++) {
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
