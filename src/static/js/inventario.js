// ==================== CALCULAR TOTALES ====================
document.addEventListener('DOMContentLoaded', function() {
  calcularTotales();
});

function calcularTotales() {
  const filas = document.querySelectorAll('#tabla-inventario tbody tr');
  let totalStock = 0;
  let totalProducido = 0;
  let totalVendido = 0;
  
  filas.forEach(fila => {
    const stock = parseInt(fila.getAttribute('data-stock')) || 0;
    const producido = parseInt(fila.querySelector('.numero-producido').textContent) || 0;
    const vendido = parseInt(fila.querySelector('.numero-vendido').textContent) || 0;
    
    totalStock += stock;
    totalProducido += producido;
    totalVendido += vendido;
  });
  
  document.getElementById('total-stock').textContent = totalStock;
  document.getElementById('total-producido').textContent = totalProducido;
  document.getElementById('total-vendido').textContent = totalVendido;
}

// ==================== BUSCADOR ====================
const buscador = document.getElementById('buscador-inventario');
const filas = document.querySelectorAll('#tabla-inventario tbody tr');
const mensaje = document.getElementById('no-result-inventario');

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

// ==================== MODAL DE DETALLE ====================
// ==================== MODAL DE DETALLE ====================
document.addEventListener('DOMContentLoaded', function() {
  calcularTotales();
  
  // Event listener para botones de detalle
  const botonesDetalle = document.querySelectorAll('.btn-detalle');
  botonesDetalle.forEach(btn => {
    btn.addEventListener('click', function() {
      const idCultivo = this.getAttribute('data-id-cultivo');
      const nombreCultivo = this.getAttribute('data-nombre-cultivo');
      verDetalle(idCultivo, nombreCultivo);
    });
  });
});

function verDetalle(idCultivo, nombreCultivo) {
  document.getElementById('modal-titulo').textContent = `Historial: ${nombreCultivo}`;
  document.getElementById('modal-detalle').style.display = 'flex';
  document.body.style.overflow = 'hidden';
  
  cargarDetalle(idCultivo);
}

function cerrarModal() {
  document.getElementById('modal-detalle').style.display = 'none';
  document.body.style.overflow = 'auto';
}

function cargarDetalle(idCultivo) {
  const historialProduccion = document.getElementById('historial-produccion');
  const historialVentas = document.getElementById('historial-ventas');
  
  historialProduccion.innerHTML = '<p class="texto-cargando">Cargando producciones...</p>';
  historialVentas.innerHTML = '<p class="texto-cargando">Cargando ventas...</p>';
  
  fetch(`/detalle_inventario/${idCultivo}`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Mostrar producciones
        if (data.producciones.length === 0) {
          historialProduccion.innerHTML = '<p class="sin-historial">No hay producciones registradas</p>';
        } else {
          let htmlProd = '';
          data.producciones.forEach(prod => {
            htmlProd += `
              <div class="historial-item">
                <div class="historial-header">
                  <span class="historial-fecha">
                    <i class="fa-solid fa-calendar"></i> ${prod.fecha}
                  </span>
                  <span class="historial-cantidad">
                    +${prod.cantidad} bultos
                  </span>
                </div>
                <div class="historial-detalle">
                  Registrado por: ${prod.registrado_por}
                </div>
              </div>
            `;
          });
          historialProduccion.innerHTML = htmlProd;
        }
        
        // Mostrar ventas
        if (data.ventas.length === 0) {
          historialVentas.innerHTML = '<p class="sin-historial">No hay ventas registradas</p>';
        } else {
          let htmlVent = '';
          data.ventas.forEach(venta => {
            htmlVent += `
              <div class="historial-item">
                <div class="historial-header">
                  <span class="historial-fecha">
                    <i class="fa-solid fa-calendar"></i> ${venta.fecha}
                  </span>
                  <span class="historial-cantidad">
                    -${venta.cantidad} bultos
                  </span>
                </div>
                <div class="historial-detalle">
                  Precio: $${venta.precio.toLocaleString('es-CO')} | ${venta.descripcion}
                </div>
              </div>
            `;
          });
          historialVentas.innerHTML = htmlVent;
        }
      } else {
        historialProduccion.innerHTML = '<p class="sin-historial">Error al cargar historial</p>';
        historialVentas.innerHTML = '<p class="sin-historial">Error al cargar historial</p>';
      }
    })
    .catch(error => {
      console.error('Error:', error);
      historialProduccion.innerHTML = '<p class="sin-historial">Error al cargar historial</p>';
      historialVentas.innerHTML = '<p class="sin-historial">Error al cargar historial</p>';
    });
}

// Cerrar modal al hacer clic fuera
document.getElementById('modal-detalle').addEventListener('click', function(e) {
  if (e.target === this) {
    cerrarModal();
  }
});