// Array para almacenar los insumos agregados
let insumosAgregados = [];

// Función para agregar los insumos seleccionados
function agregarInsumosSeleccionados() {
    const select = document.getElementById('tipo_insumo');
    const opciones = select.selectedOptions;
    
    if (opciones.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'Atención',
            text: 'Por favor selecciona al menos un insumo'
        });
        return;
    }
    
    for (let opcion of opciones) {
        // Verificar si ya está agregado
        if (!insumosAgregados.find(i => i.value === opcion.value)) {
            insumosAgregados.push({
                value: opcion.value,
                nombre: opcion.text
            });
        }
    }
    
    // Limpiar selección
    select.selectedIndex = -1;
    
    // Mostrar los insumos
    mostrarInsumos();
}

// Función para mostrar los insumos agregados
function mostrarInsumos() {
    const container = document.getElementById('insumosSeleccionados');
    
    if (insumosAgregados.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<div class="lista-insumos"><h3>Insumos Seleccionados:</h3>';
    
    insumosAgregados.forEach((insumo, index) => {
        html += `
            <div class="insumo-item">
                <div class="insumo-nombre">
                    <strong>${insumo.nombre}</strong>
                </div>
                
                <div class="insumo-controles">
                    <div class="cantidad">
                        <label>Cantidad:</label>
                        <input type="number" 
                               name="cantidad_${insumo.value}" 
                               class="input-cantidad" 
                               placeholder="0" 
                               min="0.01"
                               step="0.01"
                               required>
                    </div>
                    
                    <div class="unidad">
                        <label>Unidad:</label>
                        <select name="unidad_${insumo.value}" class="select-unidad" required>
                            <option value="">Seleccionar</option>
                            <option value="kg">Kilogramos (kg)</option>
                            <option value="litros">Litros (L)</option>
                            <option value="unidades">Unidades</option>
                            <option value="bultos">Bultos</option>
                            <option value="cajas">Cajas</option>
                            <option value="toneladas">Toneladas (t)</option>
                        </select>
                    </div>
                    
                    <button type="button" 
                            class="btn-eliminar" 
                            onclick="eliminarInsumo(${index})"
                            title="Eliminar">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
                
                <div class="observaciones-group">
                    <label>Observaciones:</label>
                    <textarea name="observaciones_${insumo.value}" 
                              class="textarea-observaciones" 
                              rows="2" 
                              placeholder="Escribe observaciones específicas para este insumo..."></textarea>
                </div>
                
                <input type="hidden" name="insumo_value[]" value="${insumo.value}">
                <input type="hidden" name="insumo_nombre[]" value="${insumo.nombre}">
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Función para eliminar un insumo
function eliminarInsumo(index) {
    insumosAgregados.splice(index, 1);
    mostrarInsumos();
}

// Validación del formulario antes de enviar
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('formSolicitud');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            if (insumosAgregados.length === 0) {
                e.preventDefault();
                Swal.fire({
                    icon: 'warning',
                    title: 'Atención',
                    text: 'Debes agregar al menos un insumo para hacer la solicitud'
                });
                return false;
            }
        });
    }
    
    // Manejo de mensajes flash
    const flashData = document.getElementById('flash-data');
    if (flashData) {
        const icon = flashData.getAttribute('data-icon');
        const message = flashData.getAttribute('data-message');
        Swal.fire({
            icon: icon,
            title: icon === 'success' ? '¡Éxito!' : 'Atención',
            text: message
        });
    }
});