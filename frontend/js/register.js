document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            utils.hideError('errorMsg');
            
            const btn = document.getElementById('submitBtn');
            const originalText = btn.textContent;
            btn.textContent = "Enrolling User...";
            btn.disabled = true;

            const fullName = document.getElementById('fullName').value;
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if(password.length < 4) {
                utils.showError('errorMsg', "Password/MPIN must be at least 4 characters.");
                btn.textContent = originalText;
                btn.disabled = false;
                return;
            }

            const requestBody = {
                full_name: fullName,
                username: username,
                password: password
            };

            try {
                const response = await fetch(`${API_BASE_URL}/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestBody)
                });

                const data = await response.json();

                if (!response.ok) {
                    utils.showError('errorMsg', data.detail || "Registration failed.");
                    btn.textContent = originalText;
                    btn.disabled = false;
                    return;
                }

                // Show success
                btn.style.backgroundColor = "var(--accent)";
                btn.textContent = "Enrollment Complete!";
                
                setTimeout(() => {
                    window.location.href = "login.html";
                }, 1500);

            } catch (error) {
                console.error("Registration Error:", error);
                utils.showError('errorMsg', "Server error. Is the backend running?");
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    }
});
