document.addEventListener('DOMContentLoaded', () => {
    const buscador = document.getElementById('buscador-siembra');
    const tarjetas = document.querySelectorAll('.evidencia-card');
    const noResults = document.getElementById('no-result-evidencia');

    buscador.addEventListener('input', () => {
        const filtro = buscador.value.toLowerCase().trim();
        let coincidencias = 0;

        tarjetas.forEach(card => {
            const texto = card.textContent.toLowerCase();
            const show = texto.includes(filtro);

            card.style.display = show ? 'block' : 'none';
            if (show) coincidencias++;
        });

        noResults.style.display = coincidencias === 0 ? 'block' : 'none';
    });
});
