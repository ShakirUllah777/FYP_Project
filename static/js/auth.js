document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('auth-container');
    const signUpBtn = document.getElementById('signUp');
    const signInBtn = document.getElementById('signIn');
    
    const mobileToSignUp = document.getElementById('mobileToSignUp');
    const mobileToSignIn = document.getElementById('mobileToSignIn');

    // Password validation elements
    const passwordInput = document.getElementById('id_password');
    const strengthBar = document.getElementById('password-strength-bar');
    const strengthText = document.getElementById('password-strength-text');
    const confirmPasswordInput = document.getElementById('id_confirm_password');
    const matchText = document.getElementById('password-match-text');

    // Auto-dismiss alert messages after 3 seconds
    const alerts = document.querySelectorAll('.auth-alert');
    if (alerts.length > 0) {
        setTimeout(function () {
            alerts.forEach(function (alertItem) {
                alertItem.classList.add('fade-out');
                setTimeout(function () {
                    if (alertItem) {
                        alertItem.style.display = 'none';
                    }
                    if (alertItem && alertItem.parentNode && alertItem.parentNode.classList.contains('w-100')) {
                        alertItem.parentNode.style.display = 'none';
                    }
                }, 500);
            });
        }, 3000);
    }

    // Slide panel functionality
    function activateSignUp() {
        if (container) {
            container.classList.add('right-panel-active');
            history.pushState(null, '', '/register/');
        }
    }

    function activateSignIn() {
        if (container) {
            container.classList.remove('right-panel-active');
            history.pushState(null, '', '/login/');
        }
    }

    if (signUpBtn) signUpBtn.addEventListener('click', activateSignUp);
    if (signInBtn) signInBtn.addEventListener('click', activateSignIn);

    if (mobileToSignUp) {
        mobileToSignUp.addEventListener('click', function (e) {
            e.preventDefault();
            activateSignUp();
        });
    }

    if (mobileToSignIn) {
        mobileToSignIn.addEventListener('click', function (e) {
            e.preventDefault();
            activateSignIn();
        });
    }

    // Handle browser back/forward buttons
    window.addEventListener('popstate', function () {
        const path = window.location.pathname;
        if (container) {
            if (path.includes('/register')) {
                container.classList.add('right-panel-active');
            } else {
                container.classList.remove('right-panel-active');
            }
        }
    });


    // Password validation logic
    function checkPasswordMatch() {
        if (!passwordInput || !confirmPasswordInput || !matchText) return;

        const pswd = passwordInput.value;
        const confirmPswd = confirmPasswordInput.value;

        if (!confirmPswd) {
            matchText.textContent = '';
            matchText.className = 'mt-2 small d-block';
            confirmPasswordInput.classList.remove('is-valid', 'is-invalid');
            return;
        }

        if (pswd === confirmPswd) {
            matchText.innerHTML = '<i class="bi bi-check-circle-fill"></i> Passwords match';
            matchText.className = 'text-success mt-2 small d-block fw-bold';
            confirmPasswordInput.classList.remove('is-invalid');
            confirmPasswordInput.classList.add('is-valid');
        } else {
            matchText.innerHTML = '<i class="bi bi-x-circle-fill"></i> Passwords do not match';
            matchText.className = 'text-danger mt-2 small d-block fw-bold';
            confirmPasswordInput.classList.remove('is-valid');
            confirmPasswordInput.classList.add('is-invalid');
        }
    }

    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            const val = passwordInput.value;

            if (!val) {
                if (strengthBar) {
                    strengthBar.style.width = '0%';
                    strengthBar.className = 'progress-bar';
                }
                if (strengthText) {
                    strengthText.textContent = '';
                }
                checkPasswordMatch();
                return;
            }

            const missing = [];
            if (val.length < 8) missing.push('at least 8 characters');
            if (!/[A-Z]/.test(val)) missing.push('capital letter (A-Z)');
            if (!/[a-z]/.test(val)) missing.push('lowercase letter (a-z)');
            if (!/\d/.test(val)) missing.push('number (0-9)');
            if (!/[\W_]/.test(val)) missing.push('special symbol (!@#$...)');

            const total = 5;
            const metCount = total - missing.length;
            const score = (metCount / total) * 100;

            if (strengthBar) {
                strengthBar.style.width = score + '%';
                if (score <= 40) {
                    strengthBar.className = 'progress-bar bg-danger';
                } else if (score <= 80) {
                    strengthBar.className = 'progress-bar bg-warning';
                } else {
                    strengthBar.className = 'progress-bar bg-success';
                }
            }

            if (strengthText) {
                if (missing.length === 0) {
                    strengthText.innerHTML = '<i class="bi bi-check-circle-fill"></i> Strong password! All requirements met.';
                    strengthText.className = 'text-success mt-1 small d-block fw-bold';
                } else {
                    strengthText.innerHTML = '<i class="bi bi-exclamation-circle-fill"></i> Missing: ' + missing.join(', ');
                    strengthText.className = 'text-danger mt-1 small d-block fw-bold';
                }
            }

            checkPasswordMatch();
        });
    }

    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    }
});
