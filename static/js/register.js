
document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('id_password');
    const strengthBar = document.getElementById('password-strength-bar');
    const strengthText = document.getElementById('password-strength-text');

    passwordInput.addEventListener('input', function () {
        const val = passwordInput.value;
        let score = 0;

        if (!val) {
            strengthBar.style.width = '0%';
            strengthBar.className = 'progress-bar';
            strengthText.textContent = 'Password strength';
            strengthText.className = 'text-muted mt-1 d-block';
            return;
        }

        if (val.length >= 8) score += 25;
        if (/[A-Za-z]/.test(val)) score += 25;
        if (/\d/.test(val)) score += 25;
        if (/[\W_]/.test(val)) score += 25;

        strengthBar.style.width = score + '%';

        if (score <= 25) {
            strengthBar.className = 'progress-bar bg-danger';
            strengthText.textContent = 'Weak (add letters/numbers/symbols)';
            strengthText.className = 'text-danger mt-1 d-block fw-bold';
        } else if (score <= 50) {
            strengthBar.className = 'progress-bar bg-warning';
            strengthText.textContent = 'Fair (keep adding)';
            strengthText.className = 'text-warning mt-1 d-block fw-bold';
        } else if (score <= 75) {
            strengthBar.className = 'progress-bar bg-info';
            strengthText.textContent = 'Good (almost there)';
            strengthText.className = 'text-info mt-1 d-block fw-bold';
        } else {
            strengthBar.className = 'progress-bar bg-success';
            strengthText.textContent = 'Strong!';
            strengthText.className = 'text-success mt-1 d-block fw-bold';
        }
    });
});
