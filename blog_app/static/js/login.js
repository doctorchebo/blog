$(document).ready(function () {
    console.log("loaded");
    // JavaScript to toggle password visibility
    const passwordEye = document.getElementById("password-eye");
    const confirmPasswordEye = document.getElementById("confirm-password-eye");
  
    const passwordInput = document.getElementById("id_password"); // default id Django generates
    const confirmPasswordInput = document.getElementById("id_confirm_password"); // default id Django generates for confirm_password field
  
    // Event listener for password field
    passwordEye.addEventListener("click", function (e) {
      // toggle the type attribute
      const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
      passwordInput.setAttribute("type", type);
      // toggle the eye icon
      this.classList.toggle("fa-eye-slash");
    });
  
    // Event listener for confirm password field
    confirmPasswordEye.addEventListener("click", function (e) {
      // toggle the type attribute
      const type = confirmPasswordInput.getAttribute("type") === "password" ? "text" : "password";
      confirmPasswordInput.setAttribute("type", type);
      // toggle the eye icon
      this.classList.toggle("fa-eye-slash");
    });
});