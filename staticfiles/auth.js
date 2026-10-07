// check if user is logged in
function isAuthenticated() {
    const token = localStorage.getItem('token');
    console.log('isAuthenticated check:', token ? 'Token found' : 'No token');
    return token !== null && token !== undefined;
}

// get the JWT token
function getToken() {
    const token = localStorage.getItem('token');
    console.log('getToken:', token ? 'Token retrieved' : 'No token');
    return token;
}

// store user data
function setUserData(userData) {
    localStorage.setItem('user', JSON.stringify(userData));
    console.log('setUserData: User data stored', userData);
}

// get user data
function getUserData() {
    const user = localStorage.getItem('user');
    const userData = user ? JSON.parse(user) : null;
    console.log('getUserData:', userData ? 'User data found' : 'No user data');
    return userData;
}

// the logout flow.session terminator
function logout() {
    console.log('logout: Clearing session');
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
        const apiBase = (window.location.protocol.startsWith('http') && !['5500', '3000', '5173'].includes(window.location.port))
            ? window.location.origin
            : 'http://localhost:8080';
        fetch(`${apiBase}/api/auth/logout/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        }).catch(() => {});
    }
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

// Automatically refresh token when access token expires
async function refreshTokenIfNeeded() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return null;

    try {
        console.log('refreshTokenIfNeeded: Attempting token refresh...');
        const apiBase = (window.location.protocol.startsWith('http') && !['5500', '3000', '5173'].includes(window.location.port))
            ? window.location.origin
            : 'http://localhost:8080';
        const response = await fetch(`${apiBase}/api/auth/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            const newToken = data.access || data.token;
            if (newToken) {
                console.log('refreshTokenIfNeeded: Token refreshed successfully');
                localStorage.setItem('token', newToken);
                if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
                return newToken;
            }
        } else {
            console.warn('refreshTokenIfNeeded: Refresh failed with status', response.status);
        }
    } catch (e) {
        console.warn('refreshTokenIfNeeded: Network error during refresh', e);
    }
    return null;
}

// fetch current user data from backend with auto-refresh resilience
async function fetchCurrentUser() {
    try {
        let token = getToken();
        if (!token) {
            console.log('fetchCurrentUser: No token available');
            return null;
        }

        console.log('fetchCurrentUser: Fetching from backend...');
        const apiBase = (window.location.protocol.startsWith('http') && !['5500', '3000', '5173'].includes(window.location.port))
            ? window.location.origin
            : 'http://localhost:8080';

        let response = await fetch(`${apiBase}/api/auth/me/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        // If 401 Unauthorized, attempt refresh
        if (response.status === 401) {
            console.log('fetchCurrentUser: 401 received, attempting refresh...');
            const refreshedToken = await refreshTokenIfNeeded();
            if (refreshedToken) {
                token = refreshedToken;
                response = await fetch(`${apiBase}/api/auth/me/`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
            }
        }

        console.log('fetchCurrentUser: Response status', response.status);
        if (response.ok) {
            const data = await response.json();
            setUserData(data);
            return data;
        } else if (response.status === 401) {
            console.warn('fetchCurrentUser: Token expired and could not be refreshed');
            return null;
        } else {
            console.warn('fetchCurrentUser: Server response not ok', response.status);
            // Return cached user if server returned a 5xx error or rate limit
            return getUserData();
        }
    } catch (error) {
        console.error('Error fetching current user (network glitch):', error);
        // Do not invalidate session on network error! Return cached user data
        return getUserData();
    }
}

async function updateAuthUI() {
    console.log('updateAuthUI: Starting...');
    const loginBtn = document.querySelector('.login-btn');
    const nav = document.querySelector('nav');
    
    if (!nav) {
        console.log('updateAuthUI: No nav element, skipping');
        return;
    }
    
    if (isAuthenticated()) {
        console.log('updateAuthUI: User is authenticated');
        let userData = getUserData();
        if (!userData) {
            console.log('updateAuthUI: No user data in localStorage, fetching from backend');
            userData = await fetchCurrentUser();
        } else {
            // Re-validate in background without blocking or terminating
            fetchCurrentUser().catch(() => {});
        }
        
        // Only log out if token is missing or refresh has explicitly failed and no user data
        if (!userData && !getToken()) {
            console.log('updateAuthUI: No valid session, clearing');
            logout();
            return;
        }
        
        console.log('updateAuthUI: User data:', userData);
        
        if (loginBtn) {
            loginBtn.style.display = 'none';
        }

        const signupBtn = document.querySelector('.navbar-right .signup-btn');
        if (signupBtn) {
            signupBtn.style.display = 'none';
        }

        const desktopLogoutBtn = document.getElementById('desktopLogoutBtn');
        if (desktopLogoutBtn) {
            desktopLogoutBtn.style.display = 'inline-flex';
        }
        
        // add property link if user is a landlord
        const existingAddPropertyLink = nav.querySelector('.add-property-link');
        if (userData.role === 'landlord' && !existingAddPropertyLink) {
            console.log('updateAuthUI: User is landlord, adding Add Property link');
            const addPropertyLink = document.createElement('a');
            addPropertyLink.href = 'add-property.html';
            addPropertyLink.setAttribute('hx-get', 'add-property.html');
            addPropertyLink.textContent = 'Add Property';
            addPropertyLink.classList.add('add-property-link');
            nav.appendChild(addPropertyLink);
            if (window.htmx) {
                window.htmx.process(nav);
            }
        }
    } else {
        console.log('updateAuthUI: User is not authenticated');
        if (loginBtn) {
            loginBtn.style.display = 'inline-flex';
        }
        const signupBtn = document.querySelector('.navbar-right .signup-btn');
        if (signupBtn) {
            signupBtn.style.display = 'inline-flex';
        }
        const desktopLogoutBtn = document.getElementById('desktopLogoutBtn');
        if (desktopLogoutBtn) {
            desktopLogoutBtn.style.display = 'none';
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOMContentLoaded: Initializing auth UI');
    await updateAuthUI();
});
