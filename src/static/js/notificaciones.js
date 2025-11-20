document.addEventListener('DOMContentLoaded', function () {
    const flashData = document.getElementById('flash-data');
    if (flashData) {
        const icon = flashData.getAttribute('data-icon');
        const message = flashData.getAttribute('data-message');
        Swal.fire({
            icon: icon,
            title: icon === 'success' ? '¡Éxito!' : 'Error',
            text: message,
            confirmButtonColor: '#667eea'
        });
    }
});