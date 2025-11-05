document.addEventListener('DOMContentLoaded', () => {
    const body = document.getElementById('page-body');
    const themeButton = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');

    // 1. FUNCIÓN para aplicar el tema y actualizar el icono
    function applyTheme(theme) {
        // Elimina ambas clases de tema para empezar de cero
        body.classList.remove('light-theme', 'dark-theme'); 
        
        // Aplica el tema
        body.classList.add(theme); 
        
        // Actualiza el icono y el texto (opcional)
        if (theme === 'light-theme') {
            if (themeIcon) {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
            }
        } else { // 'dark-theme'
            if (themeIcon) {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
            }
        }
        
        // Guarda la preferencia en el navegador
        localStorage.setItem('theme', theme);
    }

    // 2. APLICAR TEMA AL CARGAR LA PÁGINA
    // Recupera el tema guardado, o usa 'dark-theme' como valor por defecto
    const savedTheme = localStorage.getItem('theme') || 'dark-theme'; 
    applyTheme(savedTheme);


    // 3. CAMBIAR TEMA AL HACER CLIC
    if (themeButton) {
        themeButton.addEventListener('click', () => {
            const currentTheme = body.classList.contains('dark-theme') ? 'dark-theme' : 'light-theme';
            
            // Si está en oscuro, cambia a claro, y viceversa
            const newTheme = currentTheme === 'dark-theme' ? 'light-theme' : 'dark-theme';
            
            applyTheme(newTheme);
        });
    }
});