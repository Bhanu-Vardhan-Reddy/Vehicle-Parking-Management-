<template>
  <div>
    <!-- Navbar -->
    <nav class="navbar navbar-dark bg-dark">
      <div class="container-fluid">
        <span class="navbar-brand">🚗 User Dashboard</span>
        <div class="d-flex align-items-center text-white">
          <span class="me-3">{{ user.username || user.email }}</span>
          <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
        </div>
      </div>
    </nav>

    <div class="container mt-4">
      <h2 class="mb-4">User Dashboard</h2>
      
      <!-- Coming Soon Message -->
      <div class="alert alert-info">
        <h4>🚧 Under Construction</h4>
        <p>User features coming in Milestone 4:</p>
        <ul>
          <li>View available parking lots</li>
          <li>Book parking spot</li>
          <li>Release parking spot</li>
          <li>View booking history</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserDashboard',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/')
    }
  }
}
</script>

