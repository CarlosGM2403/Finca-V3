function togglePassword() {
  const passwordInput = document.getElementById("password");
  const toggleButton = document.querySelector(".toggle-password");

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    toggleButton.textContent = "ocultar";
  } else {
    passwordInput.type = "password";
    toggleButton.textContent = "👁";
  }
}
