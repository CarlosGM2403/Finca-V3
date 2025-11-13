// ==================== BUSCADOR ====================
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


// ==================== OBSERVACIONES ====================
let idTratamientoActual = null;

// Event listener para los botones de observaciones
document.addEventListener('DOMContentLoaded', function() {
  const botonesObservaciones = document.querySelectorAll('.btn-observaciones');
  
  botonesObservaciones.forEach(btn => {
    btn.addEventListener('click', function() {
      const idTratamiento = this.getAttribute('data-id-tratamiento');
      verObservaciones(idTratamiento);
    });
  });
  
  // Contador de caracteres
  const textareaObservacion = document.getElementById('nueva-observacion');
  const contadorCaracteres = document.getElementById('contador');

  if (textareaObservacion) {
    textareaObservacion.addEventListener('input', function() {
      const longitud = this.value.length;
      contadorCaracteres.textContent = longitud;
      
      if (longitud >= 5) {
        contadorCaracteres.style.color = '#4db856';
      } else {
        contadorCaracteres.style.color = '#ff4444';
      }
    });
  }

  // Enviar observación
  const formObservacion = document.getElementById('form-observacion');
  if (formObservacion) {
    formObservacion.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const observacion = document.getElementById('nueva-observacion').value.trim();
      
      if (observacion.length < 5) {
        alert('La observación debe tener al menos 5 caracteres');
        return;
      }
      
      const formData = new FormData(this);
      
      fetch('/agregar_observacion', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert('Observación agregada correctamente');
          document.getElementById('nueva-observacion').value = '';
          document.getElementById('contador').textContent = '0';
          cargarObservaciones(idTratamientoActual);
          
          // Actualizar contador en la tabla
          const fila = document.querySelector(`tr[data-id-tratamiento="${idTratamientoActual}"]`);
          const badge = fila.querySelector('.badge-observaciones');
          badge.textContent = parseInt(badge.textContent) + 1;
        } else {
          alert('Error: ' + data.error);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Error al agregar la observación');
      });
    });
  }

  // Cerrar modal al hacer clic fuera
  const modalObservaciones = document.getElementById('modal-observaciones');
  if (modalObservaciones) {
    modalObservaciones.addEventListener('click', function(e) {
      if (e.target === this) {
        cerrarModal();
      }
    });
  }
});

// Función para abrir el modal y cargar observaciones
function verObservaciones(idTratamiento) {
  idTratamientoActual = idTratamiento;
  
  //ambos campos hidden (uno para ver, otro para enviar)
  document.getElementById('id_tratamiento_modal').value = idTratamiento;
  
  const formInput = document.getElementById('id_tratamiento_form');
  if (formInput) {
    formInput.value = idTratamiento;
  }
  
  document.getElementById('modal-observaciones').style.display = 'flex';
  document.body.style.overflow = 'hidden';
  
  cargarObservaciones(idTratamiento);
}

// Función para cerrar el modal
function cerrarModal() {
  document.getElementById('modal-observaciones').style.display = 'none';
  document.body.style.overflow = 'auto';
  const textareaObservacion = document.getElementById('nueva-observacion');
  if (textareaObservacion) {
    textareaObservacion.value = '';
    document.getElementById('contador').textContent = '0';
  }
}

// Función para cargar observaciones
function cargarObservaciones(idTratamiento) {
  const listaObservaciones = document.getElementById('lista-observaciones');
  listaObservaciones.innerHTML = '<p class="texto-cargando">Cargando observaciones...</p>';
  
  fetch(`/obtener_observaciones/${idTratamiento}`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        if (data.observaciones.length === 0) {
          listaObservaciones.innerHTML = '<p class="sin-observaciones">No hay observaciones registradas aún.</p>';
        } else {
          let html = '';
          data.observaciones.forEach(obs => {
            html += `
              <div class="observacion-item">
                <div class="observacion-header">
                  <span class="observacion-usuario"><i class="fa-solid fa-user"></i> ${obs.usuario}</span>
                  <span class="observacion-fecha"><i class="fa-solid fa-clock"></i> ${obs.fecha}</span>
                </div>
                <div class="observacion-texto">${obs.observacion}</div>
              </div>
            `;
          });
          listaObservaciones.innerHTML = html;
        }
      } else {
        listaObservaciones.innerHTML = '<p class="error-observaciones">Error al cargar observaciones.</p>';
      }
    })
    .catch(error => {
      console.error('Error:', error);
      listaObservaciones.innerHTML = '<p class="error-observaciones">Error al cargar observaciones.</p>';
    });
}