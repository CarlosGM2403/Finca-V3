// Preview de imagen de perfil
document.addEventListener('DOMContentLoaded', function() {
    const inputFoto = document.getElementById('foto_perfil');
    const previewFoto = document.getElementById('preview-foto');
    const btnCambiarFoto = document.querySelector('.btn-cambiar-foto');

    // Preview de imagen cuando se selecciona un archivo
    if (inputFoto) {
        inputFoto.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validar tamaño del archivo (máximo 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('La imagen es demasiado grande. Máximo 5MB permitido.');
                    this.value = '';
                    return;
                }

                // Validar tipo de archivo
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Formato no permitido. Use JPG, PNG o GIF.');
                    this.value = '';
                    return;
                }

                // Mostrar preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewFoto.src = e.target.result;
                    previewFoto.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Al hacer clic en "Cambiar foto", activar el input file
    if (btnCambiarFoto) {
        btnCambiarFoto.addEventListener('click', function(e) {
            e.preventDefault();
            inputFoto.click();
        });
    }

    // Validación del formulario antes de enviar
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const fullname = document.getElementById('fullname').value.trim();
            
            if (!fullname) {
                e.preventDefault();
                alert('El nombre completo es obligatorio.');
                return;
            }

            // Mostrar loading al enviar
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = 'Guardando...';
                submitBtn.disabled = true;
            }
        });
    }

    // Efectos visuales para la foto de perfil
    if (previewFoto) {
        previewFoto.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            this.style.transition = 'transform 0.3s ease';
        });

        previewFoto.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    }
});

// Función para eliminar foto de perfil (opcional)
function eliminarFotoPerfil() {
    if (confirm('¿Estás seguro de que quieres eliminar tu foto de perfil?')) {
        // Aquí podrías hacer una petición AJAX para eliminar la foto
        const previewFoto = document.getElementById('preview-foto');
        const inputFoto = document.getElementById('foto_perfil');
        
        // Restablecer a imagen por defecto
        previewFoto.src = "{{ url_for('static', filename='img/default-avatar.png') }}";
        
        // Limpiar input file
        if (inputFoto) {
            inputFoto.value = '';
        }
        
        // Aquí podrías agregar una petición fetch para eliminar la foto del servidor
        console.log('Foto eliminada (lógica backend pendiente)');
    }
}