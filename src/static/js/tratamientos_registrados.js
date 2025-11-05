const buscador = document.getElementById('buscador-tratamientos');
const filas = document.querySelectorAll('#tabla-tratamientos tbody tr');
const mensaje = document.getElementById('no-result-siembra');

buscador.addEventListener('input', () => {
  const texto = buscador.value.toLowerCase();
  let algunaVisible = false;

  filas.forEach(fila => {
    const coincide = fila.textContent.toLowerCase().includes(texto);
    fila.style.display = coincide ? '' : 'none';
    if (coincide) {
      algunaVisible = true;
    }
  });

  mensaje.style.display = algunaVisible ? 'none' : 'block';
});