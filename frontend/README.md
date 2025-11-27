# 🎨 Vehicle Parking System - Frontend

Vue.js 3 frontend application for the Vehicle Parking Management System with Bootstrap 5 styling.

## 📋 Overview

Modern, responsive single-page application (SPA) providing intuitive interfaces for both administrators and end-users to manage parking operations.

---

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🌐 Access URLs

- **Frontend Dev**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Vue DevTools**: Available in Chrome/Firefox

---

## 🏗️ Project Structure

```
frontend/
├── public/
│   └── index.html              # HTML entry point
│
├── src/
│   ├── components/
│   │   ├── Login.vue           # Authentication page (Login/Register)
│   │   ├── AdminDashboard.vue  # Admin control panel
│   │   └── UserDashboard.vue   # User booking interface
│   │
│   ├── App.vue                 # Root component with navigation
│   └── main.js                 # Entry point with Vue Router setup
│
├── package.json                # Dependencies and scripts
├── vite.config.js              # Vite configuration
└── README.md                   # This file
```

---

## 🎯 Components Overview

### 1. Login.vue
**Purpose**: User authentication and registration

**Features**:
- Toggle between Login and Register modes
- Form validation
- JWT token management
- Automatic redirect based on user role
- Error handling with user-friendly messages

**Routes**:
- `/` - Login/Register page (default)

**API Calls**:
- `POST /auth/login` - User/Admin login
- `POST /auth/register` - New user registration

---

### 2. AdminDashboard.vue
**Purpose**: Administrative control panel

**Features**:
- **Parking Lot Management**
  - Create new lots with capacity and pricing
  - Edit existing lots
  - Delete lots (with validation)
  - View all lots in card grid
  
- **Parking Spot Monitoring**
  - Real-time spot status (Available/Occupied)
  - Color-coded indicators (Green=Available, Red=Occupied)
  - Filterable by parking lot
  - Grid layout with spot numbers

- **User Management**
  - View all registered users
  - Display user statistics (total bookings, spending)
  - Search and filter capabilities

- **Email Notifications**
  - Trigger daily reminders to inactive users
  - Send monthly reports to all users
  - Export complete system data to admin email

- **Analytics & Charts**
  - System-wide occupancy rates
  - Revenue statistics per lot
  - User activity metrics

**Routes**:
- `/admin` - Admin dashboard

**API Calls**:
- `GET /api/lots` - Fetch all parking lots
- `POST /api/lots` - Create new lot
- `PUT /api/lots/:id` - Update lot
- `DELETE /api/lots/:id` - Delete lot
- `GET /api/spots/:lot_id` - Get spots for a lot
- `GET /api/users` - Fetch all users
- `POST /api/admin/send-daily-reminder` - Trigger reminders
- `POST /api/admin/send-monthly-report` - Trigger reports
- `POST /api/admin/export-all-data` - Export system data

**UI Sections**:
1. **Manage Parking Lots** - CRUD operations
2. **View Parking Spots** - Real-time status grid
3. **Registered Users** - User list with stats
4. **Email Notifications** - Manual trigger buttons
5. **System Analytics** - Charts and metrics

---

### 3. UserDashboard.vue
**Purpose**: User booking and history interface

**Features**:
- **Available Parking Lots**
  - Browse all parking lots
  - View capacity, pricing, and availability
  - Filter by location or price
  - Real-time availability updates

- **Booking System**
  - **Instant Booking**: Book now and occupy immediately
  - **Reserved Booking**: Schedule for future date/time
  - Automatic spot allocation (no manual selection)
  - Booking confirmation display
  - Active booking management

- **Release/Vacate**
  - Release active bookings
  - Automatic cost calculation
  - Instant spot availability update

- **Booking History**
  - View past and active bookings
  - Sort by date, cost, or status
  - Display detailed information:
    - Parking lot name
    - Spot number
    - Start/End times
    - Duration
    - Total cost
    - Status

- **CSV Export**
  - Export booking history to CSV
  - Email delivery notification
  - Downloadable attachment

- **Personal Analytics**
  - Monthly booking trends
  - Spending analysis
  - Most-used parking lots

**Routes**:
- `/user` - User dashboard

**API Calls**:
- `GET /api/lots` - Fetch available lots
- `GET /api/spots/:lot_id` - Check spot availability
- `POST /api/book` - Book a parking spot
- `POST /api/release/:booking_id` - Release/vacate spot
- `GET /api/bookings` - Fetch user's booking history
- `GET /api/export` - Trigger CSV export

**UI Sections**:
1. **Available Parking Lots** - Browse and book
2. **My Active Bookings** - Current reservations
3. **Booking History** - Past bookings with export
4. **Personal Statistics** - Usage analytics

---

## 🔐 Authentication Flow

### Login Process
```javascript
1. User enters credentials
2. POST /auth/login with { email, password }
3. Backend validates and returns { token, user }
4. Frontend stores token in localStorage
5. Set Authorization header for future requests
6. Redirect based on role:
   - Admin → /admin
   - User → /user
```

### Token Management
```javascript
// Store token
localStorage.setItem('token', response.data.token)

// Set axios default header
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

// Check authentication
const token = localStorage.getItem('token')
if (!token) {
  router.push('/')
}

// Logout
localStorage.removeItem('token')
delete axios.defaults.headers.common['Authorization']
router.push('/')
```

---

## 🎨 Styling Guide

### Bootstrap 5 Components Used

- **Layout**: Container, Grid System (12-column)
- **Components**: Cards, Buttons, Forms, Modals, Badges, Tables
- **Utilities**: Spacing (m-*, p-*), Colors (bg-*, text-*), Display

### Color Scheme

| Purpose | Bootstrap Class | Hex | Usage |
|---------|----------------|-----|-------|
| Primary | `btn-primary`, `bg-primary` | #0d6efd | Primary actions, headers |
| Success | `btn-success`, `bg-success` | #198754 | Available spots, success messages |
| Danger | `btn-danger`, `bg-danger` | #dc3545 | Occupied spots, delete actions |
| Warning | `btn-warning`, `bg-warning` | #ffc107 | Warnings, processing states |
| Secondary | `btn-secondary`, `bg-secondary` | #6c757d | Cancel actions, metadata |
| Light | `bg-light` | #f8f9fa | Card backgrounds, page background |

### Typography

```css
/* System Font Stack */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
             "Helvetica Neue", Arial, sans-serif;

/* Headings */
h1: 2.5rem (40px)
h2: 2.0rem (32px)
h3: 1.75rem (28px)
h5: 1.25rem (20px)

/* Body */
body: 1rem (16px)
```

---

## 📡 API Integration

### Axios Configuration

```javascript
import axios from 'axios'

axios.defaults.baseURL = 'http://localhost:5000'

// Set token from localStorage
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}
```

### Error Handling

```javascript
try {
  const response = await axios.post('/api/book', bookingData)
  // Success handling
} catch (error) {
  if (error.response) {
    // Server responded with error
    console.error('Error:', error.response.data.message)
    alert(error.response.data.message)
  } else {
    // Network error
    console.error('Network error:', error.message)
    alert('Failed to connect to server')
  }
}
```

---

## 🚦 Routing

```javascript
const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/user',
    name: 'UserDashboard',
    component: UserDashboard,
    meta: { requiresAuth: true, role: 'user' }
  }
]
```

### Route Guards

```javascript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    // Redirect to login if not authenticated
    next('/')
  } else {
    next()
  }
})
```

---

## 🔧 Configuration

### Vite Config (`vite.config.js`)

```javascript
export default {
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
}
```

### Environment Variables

Create `.env` file:

```env
VITE_API_BASE_URL=http://localhost:5000
```

Usage:
```javascript
const API_URL = import.meta.env.VITE_API_BASE_URL
```

---

## 📦 Dependencies

```json
{
  "dependencies": {
    "vue": "^3.3.0",
    "vue-router": "^4.2.0",
    "axios": "^1.4.0",
    "bootstrap": "^5.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.0",
    "vite": "^4.3.0"
  }
}
```

---

## 🧪 Testing

### Manual Testing Checklist

**Login/Register**
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (should show error)
- [ ] Token persists after page refresh
- [ ] Logout clears token and redirects

**Admin Dashboard**
- [ ] Create new parking lot
- [ ] Edit existing lot
- [ ] Delete lot (with spots available)
- [ ] Cannot delete lot with occupied spots
- [ ] View all parking spots with correct status
- [ ] View registered users list
- [ ] Trigger email notifications

**User Dashboard**
- [ ] View available parking lots
- [ ] Book instant parking spot
- [ ] Book reserved parking spot
- [ ] Release active booking (cost calculated)
- [ ] View booking history
- [ ] Export bookings to CSV
- [ ] Cannot book when already having active booking

---

## 🚨 Common Issues

### Issue 1: CORS Error
```
Access to XMLHttpRequest blocked by CORS policy
```
**Solution**: Ensure backend has CORS enabled and includes frontend URL:
```python
# backend/config.py
CORS_ORIGINS = 'http://localhost:5173'
```

### Issue 2: Token Not Persisting
```
User logged out after refresh
```
**Solution**: Check localStorage in browser DevTools:
```javascript
// Should see 'token' in Application > Local Storage
localStorage.getItem('token')
```

### Issue 3: 401 Unauthorized
```
Request failed with status 401
```
**Solution**: 
- Token expired (re-login)
- Token not set in Authorization header
- Check: `axios.defaults.headers.common['Authorization']`

### Issue 4: Components Not Updating
```
UI doesn't reflect latest data
```
**Solution**: Check Vue reactivity:
```javascript
// Use reactive data properties
data() {
  return {
    lots: [],  // Vue will track changes
    bookings: []
  }
}
```

---

## 🎯 Best Practices

### 1. Component Structure
```javascript
export default {
  name: 'ComponentName',
  data() {
    return {
      // Reactive data
    }
  },
  methods: {
    // Functions
  },
  mounted() {
    // Lifecycle hook - fetch initial data
  }
}
```

### 2. API Calls
- Use `async/await` for cleaner code
- Always wrap in `try/catch`
- Show loading states
- Handle errors gracefully

### 3. State Management
- Use `data()` for component state
- Use `props` for parent-child communication
- Use `localStorage` for persistence

### 4. Error Handling
- Display user-friendly error messages
- Log errors to console for debugging
- Provide fallback UI for failed requests

---

## 📚 Resources

- [Vue.js 3 Documentation](https://vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [Axios Documentation](https://axios-http.com/)
- [Vite Documentation](https://vitejs.dev/)

---

## 🔗 Related Documentation

- See main **[README.md](../README.md)** for complete system documentation
- Backend API documentation: [Backend README](../backend/README.md)
- Email system documentation: Check `asynctask_demo.py` in backend

---

## 📝 Notes

- **Vue 3 Composition API**: This project uses Options API for simplicity
- **State Management**: No Vuex/Pinia needed for this application size
- **CSS Framework**: Only Bootstrap 5 is allowed (no Tailwind, custom CSS)
- **Build Tool**: Vite (faster than Vue CLI)

---

**Last Updated**: November 27, 2025  
**Frontend Version**: 1.0.0  
**Vue Version**: 3.3.0
