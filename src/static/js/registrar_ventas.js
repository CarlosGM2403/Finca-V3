// Validar stock al cambiar cantidad
document.addEventListener('DOMContentLoaded', function() {
  const selectCultivo = document.getElementById('cultivo');
  const inputCantidad = document.querySelector('input[name="cantidad_bultos"]');

  if (selectCultivo && inputCantidad) {
    inputCantidad.addEventListener('input', function() {
      const opcionSeleccionada = selectCultivo.options[selectCultivo.selectedIndex];
      const stockDisponible = parseInt(opcionSeleccionada.getAttribute('data-stock')) || 0;
      const cantidadIngresada = parseInt(this.value) || 0;
      
      if (cantidadIngresada > stockDisponible) {
        this.setCustomValidity(`Solo hay ${stockDisponible} bultos disponibles`);
        this.reportValidity();
      } else {
        this.setCustomValidity('');
      }
    });
    
    // También validar al cambiar el cultivo
    selectCultivo.addEventListener('change', function() {
      inputCantidad.value = '';
      inputCantidad.setCustomValidity('');
    });
  }
});