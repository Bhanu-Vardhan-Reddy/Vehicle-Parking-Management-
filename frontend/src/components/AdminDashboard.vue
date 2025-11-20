<template>
  <div>
    <!-- Navbar -->
    <nav class="navbar navbar-dark bg-dark">
      <div class="container-fluid">
        <span class="navbar-brand">🚗 Admin Dashboard</span>
        <div class="d-flex align-items-center text-white">
          <span class="me-3">{{ user.email }}</span>
          <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
        </div>
      </div>
    </nav>

    <div class="container-fluid mt-4">
      <h2 class="mb-4">Admin Dashboard</h2>
      
      <!-- Coming Soon Message -->
      <div class="alert alert-info">
        <h4>🚧 Under Construction</h4>
        <p>Admin features coming in Milestone 3:</p>
        <ul>
          <li>Create parking lots</li>
          <li>View all spots</li>
          <li>View all users</li>
          <li>Statistics and charts</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
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

