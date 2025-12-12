// ========== DESPLEGABLE BOTON USUARIO (DESKTOP) ==========
const usuariosBtn = document.getElementById('usuarios-btn');
const usuariosDropdown = document.getElementById('usuarios-dropdown');

if (usuariosBtn && usuariosDropdown) {
    usuariosBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        usuariosDropdown.classList.toggle('show');
    });
}

// ========== DESPLEGABLE BOTON SOLICITUDES (DESKTOP) ==========
const solicitudesBtn = document.getElementById('solicitudes-btn');
const solicitudesDropdown = document.getElementById('solicitudes-dropdown');

if (solicitudesBtn && solicitudesDropdown) {
    solicitudesBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        solicitudesDropdown.classList.toggle('show');
    });
}

// ========== DESPLEGABLE BOTON CULTIVOS (DESKTOP) ==========
const dropdownBtn = document.getElementById('dropdown-btn');
const dropdownContent = document.getElementById('dropdown-content');

if (dropdownBtn && dropdownContent) {
    dropdownBtn.addEventListener('click', function(e) {
        e.preventDefault();
        dropdownContent.classList.toggle('show');
    });
}

// ========== MENU HAMBURGUESA ==========
const toggleBtn = document.getElementById('menu-toggle');
const menu = document.getElementById('menu');

if (toggleBtn && menu) {
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.classList.toggle('show');
    });
}

// ========== DESPLEGABLES DENTRO DEL MENÚ LATERAL ==========
const menuUsuariosTrigger = document.getElementById('menu-usuarios-trigger');
const menuUsuariosContent = document.getElementById('menu-usuarios-content');
const menuSolicitudesTrigger = document.getElementById('menu-solicitudes-trigger');
const menuSolicitudesContent = document.getElementById('menu-solicitudes-content');

// Desplegable de Usuarios en menú lateral
if (menuUsuariosTrigger && menuUsuariosContent) {
    menuUsuariosTrigger.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Click en Usuarios trigger');
        
        // Toggle del menú de usuarios
        this.classList.toggle('active');
        menuUsuariosContent.classList.toggle('show');
        
        // Cerrar solicitudes si está abierto
        if (menuSolicitudesContent && menuSolicitudesContent.classList.contains('show')) {
            menuSolicitudesTrigger.classList.remove('active');
            menuSolicitudesContent.classList.remove('show');
        }
    });
}

// Desplegable de Solicitudes en menú lateral
if (menuSolicitudesTrigger && menuSolicitudesContent) {
    menuSolicitudesTrigger.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Click en Solicitudes trigger');
        
        // Toggle del menú de solicitudes
        this.classList.toggle('active');
        menuSolicitudesContent.classList.toggle('show');
        
        // Cerrar usuarios si está abierto
        if (menuUsuariosContent && menuUsuariosContent.classList.contains('show')) {
            menuUsuariosTrigger.classList.remove('active');
            menuUsuariosContent.classList.remove('show');
        }
    });
}

// Cerrar menú al hacer clic en un enlace interno
if (menuUsuariosContent) {
    const enlacesUsuarios = menuUsuariosContent.querySelectorAll('a');
    enlacesUsuarios.forEach(enlace => {
        enlace.addEventListener('click', () => {
            if (menu) menu.classList.remove('show');
        });
    });
}

if (menuSolicitudesContent) {
    const enlacesSolicitudes = menuSolicitudesContent.querySelectorAll('a');
    enlacesSolicitudes.forEach(enlace => {
        enlace.addEventListener('click', () => {
            if (menu) menu.classList.remove('show');
        });
    });
}

// ========== CERRAR DROPDOWNS AL HACER CLIC FUERA ==========
document.addEventListener('click', function(event) {
    // Cerrar menú hamburguesa
    if (menu && !event.target.closest('#menu') && !event.target.closest('#menu-toggle')) {
        menu.classList.remove('show');
        
        // Cerrar también los desplegables internos
        if (menuUsuariosContent) {
            menuUsuariosContent.classList.remove('show');
            if (menuUsuariosTrigger) menuUsuariosTrigger.classList.remove('active');
        }
        if (menuSolicitudesContent) {
            menuSolicitudesContent.classList.remove('show');
            if (menuSolicitudesTrigger) menuSolicitudesTrigger.classList.remove('active');
        }
    }
    
    // Cerrar dropdown de usuarios (desktop)
    if (usuariosDropdown && !event.target.closest('.btn-wrapper-usuarios')) {
        usuariosDropdown.classList.remove('show');
    }
    
    // Cerrar dropdown de solicitudes (desktop)
    if (solicitudesDropdown && !event.target.closest('.btn-wrapper-solicitudes')) {
        solicitudesDropdown.classList.remove('show');
    }
    
    // Cerrar dropdown de cultivos (desktop)
    if (dropdownContent && !event.target.closest('.btn-wrapper')) {
        dropdownContent.classList.remove('show');
    }
});

// DEBUG: Verificar que los elementos existen
console.log('=== VERIFICACIÓN DE ELEMENTOS ===');
console.log('Menu Usuarios Trigger:', menuUsuariosTrigger);
console.log('Menu Usuarios Content:', menuUsuariosContent);
console.log('Menu Solicitudes Trigger:', menuSolicitudesTrigger);
console.log('Menu Solicitudes Content:', menuSolicitudesContent);
console.log('Menu:', menu);