function switchForm(formType) {
    if (formType === 'login') {
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('register-form').style.display = 'none';
        document.getElementById('login-tab').classList.add('active');
        document.getElementById('register-tab').classList.remove('active');
    } else {
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('register-form').style.display = 'block';
        document.getElementById('login-tab').classList.remove('active');
        document.getElementById('register-tab').classList.add('active');
    }
}

function togglePassword(fieldId) {
    var inputField = document.getElementById(fieldId);
    var iconToggle = document.getElementById(fieldId + "-icon");
    if (inputField.type === "password") {
        inputField.type = "text";
        iconToggle.classList.remove("fa-eye");
        iconToggle.classList.add("fa-eye-slash");
    } else {
        inputField.type = "password";
        iconToggle.classList.remove("fa-eye-slash");
        iconToggle.classList.add("fa-eye");
    }
}
