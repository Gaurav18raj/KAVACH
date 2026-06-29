document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            utils.hideError('errorMsg');
            
            const btn = document.getElementById('submitBtn');
            const originalText = btn.textContent;
            btn.textContent = "Verifying Behavior...";
            btn.disabled = true;

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            // Get transaction amount for Demo purposes
            const txInput = document.getElementById('txAmount');
            const txAmount = txInput ? parseFloat(txInput.value) : 0.0;
            
            // Get behavioral data from the Kavach SDK
            const behavioralPayload = window.Kavach.getPayload(txAmount);
            console.log("Sending Payload to KAVACH Engine:", behavioralPayload);

            const requestBody = {
                username: username,
                password: password,
                behavioral_data: behavioralPayload.behavioral_data,
                device: behavioralPayload.device
            };

            try {
                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestBody)
                });

                const data = await response.json();

                if (!response.ok) {
                    utils.showError('errorMsg', data.detail || "Authentication failed.");
                    btn.textContent = originalText;
                    btn.disabled = false;
                    return;
                }

                console.log("API Risk Decision:", data);

                if (data.access_granted) {
                    utils.setToken(data.session_token);
                    utils.setUser({ 
                        username: username,
                        last_risk_score: data.risk_score,
                        last_risk_level: data.risk_level
                    });
                    
                    // Show success briefly before redirecting
                    btn.style.backgroundColor = "var(--accent)";
                    btn.textContent = `Access Granted (Risk: ${data.risk_score})`;
                    
                    setTimeout(() => {
                        window.location.href = "dashboard.html";
                    }, 1000);
                } else {
                    // Handled based on Action
                    if (data.action === "OTP_CHALLENGE") {
                        utils.showError('errorMsg', `[RISK: CHALLENGE] Unusual behavior detected. OTP Challenge required.`);
                    } else {
                        utils.showError('errorMsg', `[RISK: CRITICAL] Access Blocked. ${data.reasons.join(', ')}`);
                    }
                    btn.textContent = originalText;
                    btn.disabled = false;
                }
            } catch (error) {
                console.error("Login Error:", error);
                utils.showError('errorMsg', "Server error. Is the backend running?");
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    }
});
