document.addEventListener('DOMContentLoaded', () => {
  const buscador = document.getElementById('buscador-siembra');
  const tarjetas = document.querySelectorAll('.card');

  buscador.addEventListener('input', function () {
    const filtro = this.value.toLowerCase().trim();
    let coincidencias = 0;

    tarjetas.forEach(card => {
      const texto = card.textContent.toLowerCase();
      const coincide = texto.includes(filtro);

      card.style.display = coincide ? 'block' : 'none';
      if (coincide) coincidencias++;
    });

    // Opcional: mostrar mensaje si no hay coincidencias
    const mensaje = document.getElementById('no-result-evidencia');
    if (mensaje) {
      mensaje.style.display = (coincidencias === 0) ? 'block' : 'none';
    }
  });
});