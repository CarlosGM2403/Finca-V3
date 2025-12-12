function actualizarContadorNotificaciones() {
    fetch("/contar_notificaciones_pendientes")
        .then(response => response.json())
        .then(data => {
            const badgeFlotante = document.getElementById('badge-notificaciones-flotante');
            const badgeMenu = document.getElementById('badge-notificaciones-menu');

            if (data.count > 0) {
                if (badgeFlotante) {
                    badgeFlotante.textContent = data.count;
                    badgeFlotante.style.display = "flex";
                }
                if (badgeMenu) {
                    badgeMenu.textContent = data.count;
                    badgeMenu.style.display = "inline-block";
                }
            } else {
                if (badgeFlotante) badgeFlotante.style.display = "none";
                if (badgeMenu) badgeMenu.style.display = "none";
            }
        })
        .catch(err => console.error("Error obteniendo notificaciones:", err));
}

document.addEventListener("DOMContentLoaded", () => {
    actualizarContadorNotificaciones();
    setInterval(actualizarContadorNotificaciones, 30000);
});
