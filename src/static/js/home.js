document.addEventListener("DOMContentLoaded", () => {
  const menu = document.getElementById("menu");
  const menuBtn = document.querySelector(".menu-btn");

  // Función para mostrar/ocultar menú
  function toggleMenu() {
    menu.classList.toggle("show");
  }

  // Asignar evento al botón hamburguesa
  if (menuBtn) {
    menuBtn.addEventListener("click", (e) => {
      e.stopPropagation(); // evita que se cierre inmediatamente
      toggleMenu();
    });
  }

  // Cierra el menú si se hace clic fuera
  document.addEventListener("click", (event) => {
    if (menu.classList.contains("show") &&
        !menu.contains(event.target) &&
        !menuBtn.contains(event.target)) {
      menu.classList.remove("show");
    }
  });

  // Confirmar cierre de sesión
  window.confirmLogout = function() {
    if (confirm("¿Seguro que quieres cerrar sesión?")) {
      window.location.href = "/logout";
    }
  };
});
