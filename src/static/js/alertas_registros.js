document.addEventListener("DOMContentLoaded", function () {
    const alertElement = document.getElementById("flash-data");

    if (alertElement) {
        const message = alertElement.dataset.message;
        const icon = alertElement.dataset.icon;

        Swal.fire({
            icon: icon,
            title: message,
            timer: 2000,
            showConfirmButton: false
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
  const buscador = document.getElementById('buscador-solicitudes');

  const filtrarTabla = (tablaId) => {
    const tabla = document.getElementById(tablaId);
    if (!tabla) return 0;

    const filas = tabla.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    const filtro = buscador.value.toLowerCase().trim();
    let coincidencias = 0;

    for (let fila of filas) {
      const texto = fila.textContent.toLowerCase();
      const coincide = texto.includes(filtro);
      fila.style.display = coincide ? '' : 'none';
      if (coincide) coincidencias++;
    }

    return coincidencias;
  };

  buscador.addEventListener('input', () => {
    const total = filtrarTabla('tabla-pendientes') + filtrarTabla('tabla-procesadas');

    const mensaje = document.getElementById('no-result-solicitudes');
    const mensaje1 = document.getElementById('no-result-solicitud');
    if (mensaje) {
      mensaje.style.display = total === 0 ? 'block' : 'none';
    }
  });
});