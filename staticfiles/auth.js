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
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

// fetch current user data from backend
async function fetchCurrentUser() {
    try {
        const token = getToken();
        if (!token) {
            console.log('fetchCurrentUser: No token available');
            return null;
        }

        console.log('fetchCurrentUser: Fetching from backend...');
        const response = await fetch('http://localhost:8000/api/auth/me/', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        console.log('fetchCurrentUser: Response status', response.status);
        if (response.ok) {
            const data = await response.json();
            setUserData(data);
            return data;
        } else {
            console.error('fetchCurrentUser: Response not ok', response.status);
            return null;
        }
    } catch (error) {
        console.error('Error fetching current user:', error);
        return null;
    }
}

async function updateAuthUI() {
    console.log('updateAuthUI: Starting...');
    const loginBtn = document.querySelector('.login-btn');
    const nav = document.querySelector('nav');
    
    console.log('updateAuthUI: nav element found?', !!nav);
    console.log('updateAuthUI: loginBtn found?', !!loginBtn);
    
    if (!nav) {
        console.log('updateAuthUI: No nav element, skipping');
        return;
    }
    
    if (isAuthenticated()) {
        console.log('updateAuthUI: User is authenticated');
        // fetch fresh user data from backend
        let userData = getUserData();
        if (!userData) {
            console.log('updateAuthUI: No user data in localStorage, fetching from backend');
            userData = await fetchCurrentUser();
        }
        
        if (!userData) {
            console.log('updateAuthUI: No user data available, redirecting to login');
            // token is invalid, clear and redirect to login
            logout();
            return;
        }
        
        console.log('updateAuthUI: User data:', userData);
        
        if (loginBtn) {
            loginBtn.remove();
            console.log('updateAuthUI: Login button removed');
        }
        
        // check if auth links already exist
        const existingAccountLink = nav.querySelector('.account-link');
        const existingLogoutBtn = nav.querySelector('.logout-btn');
        const existingAddPropertyLink = nav.querySelector('.add-property-link');
        
        console.log('updateAuthUI: Existing links?', !!existingAccountLink, !!existingLogoutBtn);
        
        if (!existingAccountLink && !existingLogoutBtn) {
            console.log('updateAuthUI: Adding auth links');
            // the user profile button
            const profileBtn = document.createElement('a');
            profileBtn.href = 'account.html';
            profileBtn.textContent = 'Profile';
            profileBtn.classList.add('account-link', 'profile-btn');
            
            // add property link if user is a landlord
            if (userData.role === 'landlord') {
                console.log('updateAuthUI: User is landlord, adding Add Property link');
                const addPropertyLink = document.createElement('a');
                addPropertyLink.href = 'add-property.html';
                addPropertyLink.textContent = 'Add Property';
                addPropertyLink.classList.add('add-property-link');
                nav.appendChild(addPropertyLink);
            }
            
            //logout button
            const logoutBtn = document.createElement('a');
            logoutBtn.href = '#';
            logoutBtn.textContent = 'Logout';
            logoutBtn.classList.add('logout-btn');
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                logout();
            });
            
            nav.appendChild(profileBtn);
            nav.appendChild(logoutBtn);
            console.log('updateAuthUI: Auth links added successfully');
        } else {
            console.log('updateAuthUI: Auth links already exist, skipping');
        }
    } else {
        console.log('updateAuthUI: User is not authenticated');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOMContentLoaded: Initializing auth UI');
    await updateAuthUI();
});
