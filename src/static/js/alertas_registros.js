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