    const form = document.getElementById('cambiarPassForm');
    const errorDiv = document.getElementById('error');

    form.addEventListener('submit', function(e){
        const newPass = document.getElementById('new_password').value;
        const confirmPass = document.getElementById('confirm_password').value;

        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

        if(newPass !== confirmPass){
            e.preventDefault();
            errorDiv.textContent = "Las contraseñas no coinciden";
        } else if(!passwordRegex.test(newPass)){
            e.preventDefault();
            errorDiv.textContent = "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo";
        } else {
            errorDiv.textContent = "";
        }
    });

    function togglePassword(id){
        const input = document.getElementById(id);
        if(input.type === "password"){
            input.type = "text";
        } else {
            input.type = "password";
        }
    }
