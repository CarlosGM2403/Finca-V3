document.addEventListener('DOMContentLoaded', function() {
    // Filtrado de solicitudes
    const filtroBtns = document.querySelectorAll('.filtro-btn');
    const solicitudFilas = document.querySelectorAll('.solicitud-fila');
    
    filtroBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remover clase active de todos los botones
            filtroBtns.forEach(b => b.classList.remove('active'));
            // Agregar clase active al botón clickeado
            this.classList.add('active');
            
            const estado = this.dataset.estado;
            
            // Filtrar filas
            solicitudFilas.forEach(fila => {
                if (estado === 'todas' || fila.dataset.estado === estado) {
                    fila.style.display = '';
                    setTimeout(() => {
                        fila.style.opacity = '1';
                    }, 50);
                } else {
                    fila.style.opacity = '0';
                    setTimeout(() => {
                        fila.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
    
    // Efectos hover en filas
    solicitudFilas.forEach(fila => {
        fila.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        fila.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
});