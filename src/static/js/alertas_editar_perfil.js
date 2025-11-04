document.addEventListener("DOMContentLoaded", () => {
    const flashData = document.getElementById("flash-data");

    if (flashData) {
        const icon = flashData.getAttribute("data-icon");
        const message = flashData.getAttribute("data-message");

        Swal.fire({
            icon: icon === "error" ? "error" : "success",
            title: message,
            timer: 1800,
            showConfirmButton: false
        }).then(() => {
            if (icon === "success") {
                window.location.href = "/perfil";
            }
        });
    }
});