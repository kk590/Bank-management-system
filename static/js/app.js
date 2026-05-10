const API_URL = '/api';

function showNotification(message, type = 'success') {
    let el = document.getElementById('notification');
    if (!el) {
        el = document.createElement('div');
        el.id = 'notification';
        document.body.appendChild(el);
    }
    el.textContent = message;
    el.className = `notification notify-${type} show`;
    setTimeout(() => {
        el.classList.remove('show');
    }, 3000);
}

function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

async function fetchAPI(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    // For x-www-form-urlencoded (login)
    if (options.body instanceof URLSearchParams) {
        delete headers['Content-Type'];
    }
    
    if (token && !options.noAuth) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
        const data = await response.json();
        
        if (!response.ok) {
            // Handle 401 Unauthorized
            if (response.status === 401 && window.location.pathname !== '/') {
                logout();
                return;
            }
            throw new Error(data.detail || 'Something went wrong');
        }
        return data;
    } catch (error) {
        showNotification(error.message, 'error');
        throw error;
    }
}

// Redirect if already logged in and on index page
document.addEventListener('DOMContentLoaded', async () => {
    if (window.location.pathname === '/' && getToken()) {
        try {
            const user = await fetchAPI('/users/me');
            if (user.role === 'admin') {
                window.location.href = '/admin';
            } else {
                window.location.href = '/dashboard';
            }
        } catch (e) {
            localStorage.removeItem('token');
        }
    }
});
