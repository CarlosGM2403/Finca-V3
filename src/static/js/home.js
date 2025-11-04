// DESPLEGABLE BOTON USUARIO
const usuariosBtn = document.getElementById('usuarios-btn');
const usuariosDropdown = document.getElementById('usuarios-dropdown');

if (usuariosBtn && usuariosDropdown) {
    usuariosBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        usuariosDropdown.classList.toggle('show');
    });

    // Cierra si haces clic fuera del botón o sub-botones
    window.addEventListener('click', function(e) {
        if (!e.target.closest('.btn-wrapper-usuarios')) {
            usuariosDropdown.classList.remove('show');
        }
    });
}

// DESPLEGABLE BOTON CULTIVOS
const dropdownBtn = document.getElementById('dropdown-btn');
const dropdownContent = document.getElementById('dropdown-content');

if (dropdownBtn && dropdownContent) {
    dropdownBtn.addEventListener('click', function(e) {
        e.preventDefault();
        dropdownContent.classList.toggle('show');
    });

    // Cierra si haces clic fuera del botón o los sub-botones
    window.addEventListener('click', function(e) {
        if (!e.target.closest('.btn-wrapper')) {
            dropdownContent.classList.remove('show');
        }
    });
}

// BOTON DE LOGOUT
function confirmLogout() {
    if (confirm("¿Seguro que quieres cerrar sesión?")) {
        window.location.href = document.querySelector('.logout-btn a')?.href || "{{ url_for('logout') }}";
    }
}

// MENU HAMBURGUESA
const toggleBtn = document.getElementById('menu-toggle');
const menu = document.getElementById('menu');

if (toggleBtn && menu) {
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // evita cerrar inmediatamente al hacer clic
        menu.classList.toggle('show');
    });

    // Cerrar menú si haces clic fuera de él
    window.addEventListener('click', (e) => {
        if (!e.target.closest('#menu') && !e.target.closest('#menu-toggle')) {
            menu.classList.remove('show');
        }
    });
}

// Cerrar todos los dropdowns al hacer clic en cualquier parte
document.addEventListener('click', function(event) {
    // Cerrar menú hamburguesa
    if (menu && !event.target.closest('#menu') && !event.target.closest('#menu-toggle')) {
        menu.classList.remove('show');
    }
    
    // Cerrar dropdown de usuarios
    if (usuariosDropdown && !event.target.closest('.btn-wrapper-usuarios')) {
        usuariosDropdown.classList.remove('show');
    }
    
    // Cerrar dropdown de cultivos
    if (dropdownContent && !event.target.closest('.btn-wrapper')) {
        dropdownContent.classList.remove('show');
    }
});