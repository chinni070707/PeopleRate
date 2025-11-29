// API base URL
const API_BASE = '/api';

// Authentication token storage
let authToken = localStorage.getItem('authToken');

// Helper function to make API calls
async function apiCall(endpoint, options = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    if (authToken) {
        defaultHeaders['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: { ...defaultHeaders, ...options.headers },
        ...options
    });

    if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('authToken');
        authToken = null;
        window.location.href = '/login';
        return;
    }

    return response;
}

// Search functionality
async function searchPeople() {
    const query = document.getElementById('searchInput').value.trim();
    if (query.length < 2) {
        showAlert('Please enter at least 2 characters to search', 'error');
        return;
    }

    try {
        const response = await apiCall(`/persons/search?q=${encodeURIComponent(query)}`);
        const searchData = await response.json();
        
        displaySearchResults(searchData);
    } catch (error) {
        console.error('Search error:', error);
        showAlert('Error searching for people', 'error');
    }
}

// Display search results
function displaySearchResults(searchData = {}) {
    const resultsDiv = document.getElementById('searchResults');
    const persons = searchData.persons || [];
    const query = searchData.query || document.getElementById('searchInput').value.trim();
    
    if (persons.length === 0) {
        const message = searchData.suggest_add_person
            ? `No strong matches found for "${query}". Refine the spot (e.g., Indiranagar, Koramangala) or add the Bengaluru vendor below.`
            : 'No matches yet. Add your local vendor manually.';
        resultsDiv.innerHTML = `
            <div class="no-results-card">
                <p>${message}</p>
                <button class="btn-add-person" onclick="openAddPersonModal()">➕ Add This Person</button>
            </div>
        `;
        return;
    }

    resultsDiv.innerHTML = persons.map(person => {
        const name = person.name || person.full_name || 'Unnamed Vendor';
        const rating = person.average_rating || 0;
        const reviewCount = person.review_count || person.total_reviews || 0;
        const reviewLabel = reviewCount === 1 ? 'review' : 'reviews';
        const services = (person.services_offered || person.skills || [])
            .slice(0, 3)
            .map(service => `<span class="service-chip">${service}</span>`)
            .join('');
        const contactBits = [];
        if (person.phone) contactBits.push(`📞 ${person.phone}`);
        if (person.whatsapp_number) contactBits.push(`💬 WhatsApp ${person.whatsapp_number}`);

        return `
        <div class="person-card" onclick="viewPerson('${person.id}')">
            <div class="person-card-header">
                <div>
                    <div class="person-name">${name}</div>
                    <div class="person-local-meta">
                        ${person.category ? `<span class="person-category-pill">${person.category}</span>` : ''}
                        ${person.area ? `<span class="person-area-badge">${person.area}</span>` : ''}
                    </div>
                    <div class="person-details">
                        ${person.company ? `${person.company}` : ''}
                        ${person.city ? `• ${person.city}` : ''}
                        ${person.job_title ? `• ${person.job_title}` : ''}
                    </div>
                    ${contactBits.length ? `<div class="person-contact-line">${contactBits.join(' • ')}</div>` : ''}
                    ${services ? `<div class="person-services">${services}</div>` : ''}
                </div>
                <div class="person-rating">
                    <div>
                        <span class="stars">${generateStars(rating)}</span>
                        <div class="rating-score">${rating.toFixed(1)}</div>
                        <div class="rating-count">${reviewCount} ${reviewLabel}</div>
                    </div>
                </div>
            </div>
        </div>`;
    }).join('');
}

// Generate star rating display
function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    return '★'.repeat(fullStars) + 
           (hasHalfStar ? '☆' : '') + 
           '☆'.repeat(emptyStars);
}

// View person details
function viewPerson(personId) {
    window.location.href = `/person/${personId}`;
}

// Show alert messages
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    // Insert at the top of main content
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(alertDiv, mainContent.firstChild);
    
    // Remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Login functionality
async function login(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const loginData = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    try {
        const response = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify(loginData)
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            showAlert('Login successful!', 'success');
            
            // Redirect after short delay
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            const errorData = await response.json();
            showAlert(errorData.detail || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Error during login', 'error');
    }
}

// Register functionality
async function register(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const registerData = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        full_name: formData.get('full_name')
    };

    // Validate password confirmation
    if (registerData.password !== formData.get('confirm_password')) {
        showAlert('Passwords do not match', 'error');
        return;
    }

    try {
        const response = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify(registerData)
        });

        if (response.ok) {
            showAlert('Registration successful! Please login.', 'success');
            
            // Redirect to login after short delay
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            const errorData = await response.json();
            showAlert(errorData.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAlert('Error during registration', 'error');
    }
}

// Add person functionality
async function addPerson(event) {
    event.preventDefault();
    
    if (!authToken) {
        showAlert('Please login to add a person', 'error');
        return;
    }

    const formData = new FormData(event.target);
    const personData = {
        full_name: formData.get('full_name'),
        nickname: formData.get('nickname'),
        phone_number: formData.get('phone_number'),
        email: formData.get('email'),
        linkedin_url: formData.get('linkedin_url'),
        company: formData.get('company'),
        job_title: formData.get('job_title'),
        city: formData.get('city'),
        country: formData.get('country'),
        bio: formData.get('bio')
    };

    try {
        const response = await apiCall('/persons/', {
            method: 'POST',
            body: JSON.stringify(personData)
        });

        if (response.ok) {
            const person = await response.json();
            showAlert('Person added successfully!', 'success');
            
            // Redirect to person page
            setTimeout(() => {
                window.location.href = `/person/${person.id}`;
            }, 1000);
        } else {
            const errorData = await response.json();
            showAlert(errorData.detail || 'Failed to add person', 'error');
        }
    } catch (error) {
        console.error('Add person error:', error);
        showAlert('Error adding person', 'error');
    }
}

// Add review functionality
async function addReview(event) {
    event.preventDefault();
    
    if (!authToken) {
        showAlert('Please login to add a review', 'error');
        return;
    }

    const formData = new FormData(event.target);
    const reviewData = {
        person_id: formData.get('person_id'),
        rating: parseInt(formData.get('rating')),
        title: formData.get('title'),
        content: formData.get('content'),
        category: formData.get('category')
    };

    try {
        const response = await apiCall('/reviews/', {
            method: 'POST',
            body: JSON.stringify(reviewData)
        });

        if (response.ok) {
            showAlert('Review added successfully!', 'success');
            
            // Reload page to show new review
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            const errorData = await response.json();
            showAlert(errorData.detail || 'Failed to add review', 'error');
        }
    } catch (error) {
        console.error('Add review error:', error);
        showAlert('Error adding review', 'error');
    }
}

// Logout functionality
function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    showAlert('Logged out successfully', 'success');
    
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

// Initialize page based on authentication status
function initializePage() {
    const navMenu = document.querySelector('.nav-menu');
    
    if (authToken) {
        // User is logged in
        navMenu.innerHTML = `
            <a href="/" class="nav-link">Home</a>
            <a href="/search" class="nav-link">Search People</a>
            <a href="/add-person" class="nav-link">Add Person</a>
            <a href="/my-reviews" class="nav-link">My Reviews</a>
            <a href="#" onclick="logout()" class="nav-link">Logout</a>
        `;
    } else {
        // User is not logged in
        navMenu.innerHTML = `
            <a href="/" class="nav-link">Home</a>
            <a href="/search" class="nav-link">Search People</a>
            <a href="/login" class="nav-link">Login</a>
            <a href="/register" class="nav-link">Register</a>
        `;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initializePage);

// Allow search on Enter key
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchPeople();
            }
        });
    }
});