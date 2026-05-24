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
            let score = 0;

            if (!val) {
                if (strengthBar) {
                    strengthBar.style.width = '0%';
                    strengthBar.className = 'progress-bar';
                }
                if (strengthText) {
                    strengthText.textContent = 'Password strength';
                    strengthText.className = 'text-muted mt-1 d-block';
                }
                checkPasswordMatch();
                return;
            }

            if (val.length >= 8) score += 25;
            if (/[A-Za-z]/.test(val)) score += 25;
            if (/\d/.test(val)) score += 25;
            if (/[\W_]/.test(val)) score += 25;

            if (strengthBar) {
                strengthBar.style.width = score + '%';
            }

            if (score <= 25) {
                if (strengthBar) strengthBar.className = 'progress-bar bg-danger';
                if (strengthText) {
                    strengthText.textContent = 'Weak (add letters/numbers/symbols)';
                    strengthText.className = 'text-danger mt-1 d-block fw-bold';
                }
            } else if (score <= 50) {
                if (strengthBar) strengthBar.className = 'progress-bar bg-warning';
                if (strengthText) {
                    strengthText.textContent = 'Fair (keep adding)';
                    strengthText.className = 'text-warning mt-1 d-block fw-bold';
                }
            } else if (score <= 75) {
                if (strengthBar) strengthBar.className = 'progress-bar bg-info';
                if (strengthText) {
                    strengthText.textContent = 'Good (almost there)';
                    strengthText.className = 'text-info mt-1 d-block fw-bold';
                }
            } else {
                if (strengthBar) strengthBar.className = 'progress-bar bg-success';
                if (strengthText) {
                    strengthText.textContent = 'Strong!';
                    strengthText.className = 'text-success mt-1 d-block fw-bold';
                }
            }

            checkPasswordMatch();
        });
    }

    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    }
});
