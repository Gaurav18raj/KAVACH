/**
 * KAVACH - Shared Utilities
 */

const API_BASE_URL = "http://localhost:8000/api/v1";

const utils = {
    // Show errors on forms
    showError(msgId, message) {
        const el = document.getElementById(msgId);
        if (el) {
            el.textContent = message;
            el.classList.remove('hidden');
        }
    },
    
    hideError(msgId) {
        const el = document.getElementById(msgId);
        if (el) {
            el.classList.add('hidden');
        }
    },

    // Auth Token Management
    setToken(token) {
        localStorage.setItem('kavach_token', token);
    },

    getToken() {
        return localStorage.getItem('kavach_token');
    },

    clearToken() {
        localStorage.removeItem('kavach_token');
        localStorage.removeItem('kavach_user');
    },

    setUser(user) {
        localStorage.setItem('kavach_user', JSON.stringify(user));
    },

    getUser() {
        const user = localStorage.getItem('kavach_user');
        return user ? JSON.parse(user) : null;
    },

    // Display debug info on screen if debug panel exists
    logDebug(title, data) {
        let panel = document.getElementById('debugPanel');
        if (!panel) {
            panel = document.createElement('div');
            panel.id = 'debugPanel';
            panel.className = 'debug-panel';
            document.body.appendChild(panel);
        }

        const formattedData = JSON.stringify(data, null, 2);
        panel.innerHTML = `
            <div class="debug-title">${title}</div>
            <pre style="white-space: pre-wrap; word-wrap: break-word; color: #a5b4fc;">${formattedData}</pre>
        `;
    }
};
