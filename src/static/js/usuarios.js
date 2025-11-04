const buscador = document.getElementById('buscador');
const tabla = document.getElementById('tabla-usuarios').getElementsByTagName('tbody')[0];
const filas = tabla.getElementsByTagName('tr');
const noResult = document.getElementById('no-result');

buscador.addEventListener('input', function() {
    const filtro = this.value.toLowerCase().trim();
    let coincidencias = 0;

    for (let i = 0; i < filas.length; i++) {
        if (filas[i].id === 'no-result') continue;

        const celdas = filas[i].getElementsByTagName('td');
        let textoFila = '';
        for (let j = 0; j < celdas.length - 1; j++) {
            textoFila += celdas[j].textContent.toLowerCase() + ' ';
        }

        if (textoFila.includes(filtro)) {
            filas[i].style.display = '';
            coincidencias++;
        } else {
            filas[i].style.display = 'none';
        }
    }

    if (coincidencias === 0) {
        noResult.style.display = '';
    } else {
        noResult.style.display = 'none';
    }
});
