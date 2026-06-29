/**
 * KAVACH - Shared Utilities
 */

const API_BASE_URL = `${window.location.origin}/api/v1`;
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
        console.log(`%c[KAVACH DEBUG] %c${title}`, "color: #069; font-weight: bold;", "color: inherit;");
        console.log(data);
    }
};
