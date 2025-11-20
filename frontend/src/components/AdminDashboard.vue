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
      
      <!-- Error/Success Messages -->
      <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ error }}
        <button type="button" class="btn-close" @click="error = null"></button>
      </div>
      <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
        {{ success }}
        <button type="button" class="btn-close" @click="success = null"></button>
      </div>
      
      <!-- Statistics Cards -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h5 class="card-title">Total Lots</h5>
              <h2>{{ stats.totalLots }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h5 class="card-title">Available Spots</h5>
              <h2>{{ stats.availableSpots }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-danger text-white">
            <div class="card-body">
              <h5 class="card-title">Occupied Spots</h5>
              <h2>{{ stats.occupiedSpots }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-info text-white">
            <div class="card-body">
              <h5 class="card-title">Total Users</h5>
              <h2>{{ users.length }}</h2>
            </div>
          </div>
        </div>
      </div>

      <!-- Create Lot Form -->
      <div class="card mb-4">
        <div class="card-header">
          <h4>Create New Parking Lot</h4>
        </div>
        <div class="card-body">
          <form @submit.prevent="createLot" class="row g-3">
            <div class="col-md-4">
              <label class="form-label">Lot Name</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="newLot.name" 
                required
                placeholder="e.g., Downtown Parking"
              >
            </div>
            <div class="col-md-3">
              <label class="form-label">Capacity (spots)</label>
              <input 
                type="number" 
                class="form-control" 
                v-model="newLot.capacity" 
                min="1" 
                required
                placeholder="e.g., 10"
              >
            </div>
            <div class="col-md-3">
              <label class="form-label">Price per Hour ($)</label>
              <input 
                type="number" 
                step="0.01" 
                class="form-control" 
                v-model="newLot.price_per_hour" 
                min="0" 
                required
                placeholder="e.g., 5.00"
              >
            </div>
            <div class="col-md-2">
              <label class="form-label">&nbsp;</label>
              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? 'Creating...' : 'Create Lot' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Parking Lots Grid -->
      <div class="card mb-4">
        <div class="card-header">
          <h4>Parking Lots</h4>
        </div>
        <div class="card-body">
          <div v-if="lots.length === 0" class="text-center text-muted py-4">
            <p>No parking lots created yet. Create one above!</p>
          </div>
          <div v-else class="row">
            <div class="col-md-4" v-for="lot in lots" :key="lot.id">
              <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                  <h5 class="m-0">{{ lot.name }}</h5>
                  <button 
                    class="btn btn-sm btn-danger" 
                    @click="confirmDeleteLot(lot)"
                    :disabled="loading"
                  >
                    Delete
                  </button>
                </div>
                <div class="card-body">
                  <p><strong>Capacity:</strong> {{ lot.capacity }} spots</p>
                  <p><strong>Price:</strong> ${{ lot.price_per_hour }}/hour</p>
                  <p>
                    <strong>Available:</strong> 
                    <span class="badge bg-success">{{ lot.available_spots }}</span>
                  </p>
                  <p>
                    <strong>Occupied:</strong> 
                    <span class="badge bg-danger">{{ lot.occupied_spots }}</span>
                  </p>
                  <button 
                    class="btn btn-info btn-sm w-100" 
                    @click="viewSpots(lot.id)"
                  >
                    View Spots
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Spots Modal -->
      <div v-if="selectedLot" class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h4>Spots in {{ selectedLot.name }}</h4>
          <button class="btn btn-secondary btn-sm" @click="selectedLot = null; spots = []">
            Close
          </button>
        </div>
        <div class="card-body">
          <div class="row">
            <div 
              class="col-6 col-md-3 col-lg-2 mb-3" 
              v-for="spot in spots" 
              :key="spot.id"
            >
              <div 
                class="card text-center py-3"
                :class="spot.status === 'Available' ? 'status-available' : 'status-occupied'"
              >
                <strong>Spot #{{ spot.spot_number }}</strong>
                <small>{{ spot.status }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Users List -->
      <div class="card">
        <div class="card-header">
          <h4>Registered Users</h4>
        </div>
        <div class="card-body">
          <div v-if="users.length === 0" class="text-center text-muted py-4">
            <p>No users registered yet.</p>
          </div>
          <table v-else class="table table-striped">
            <thead>
              <tr>
                <th>Email</th>
                <th>Username</th>
                <th>Total Bookings</th>
                <th>Active Bookings</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.email }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.total_bookings }}</td>
                <td>
                  <span class="badge bg-primary">{{ user.active_bookings }}</span>
                </td>
                <td>
                  <span 
                    class="badge" 
                    :class="user.active ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ user.active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      token: localStorage.getItem('token'),
      
      lots: [],
      users: [],
      spots: [],
      selectedLot: null,
      
      newLot: {
        name: '',
        capacity: '',
        price_per_hour: ''
      },
      
      error: null,
      success: null,
      loading: false
    }
  },
  
  computed: {
    stats() {
      return {
        totalLots: this.lots.length,
        availableSpots: this.lots.reduce((sum, lot) => sum + lot.available_spots, 0),
        occupiedSpots: this.lots.reduce((sum, lot) => sum + lot.occupied_spots, 0)
      }
    }
  },
  
  mounted() {
    this.fetchLots()
    this.fetchUsers()
  },
  
  methods: {
    async fetchLots() {
      try {
        const response = await axios.get('/api/lots', {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.lots = response.data.lots
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to fetch lots'
      }
    },
    
    async fetchUsers() {
      try {
        const response = await axios.get('/api/users', {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.users = response.data.users
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to fetch users'
      }
    },
    
    async createLot() {
      this.error = null
      this.success = null
      this.loading = true
      
      try {
        const response = await axios.post('/api/lots', this.newLot, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        
        this.success = response.data.message
        this.newLot = { name: '', capacity: '', price_per_hour: '' }
        await this.fetchLots()
        
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to create lot'
      } finally {
        this.loading = false
      }
    },
    
    confirmDeleteLot(lot) {
      if (confirm(`Are you sure you want to delete "${lot.name}"?\n\nThis will delete all ${lot.capacity} spots.`)) {
        this.deleteLot(lot.id)
      }
    },
    
    async deleteLot(lotId) {
      this.error = null
      this.success = null
      this.loading = true
      
      try {
        const response = await axios.delete(`/api/lots/${lotId}`, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        
        this.success = response.data.message
        await this.fetchLots()
        
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to delete lot'
      } finally {
        this.loading = false
      }
    },
    
    async viewSpots(lotId) {
      this.error = null
      
      try {
        const response = await axios.get(`/api/spots/${lotId}`, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        
        this.selectedLot = response.data.lot
        this.spots = response.data.spots
        
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to fetch spots'
      }
    },
    
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.status-available {
  background-color: #198754;
  color: white;
}

.status-occupied {
  background-color: #dc3545;
  color: white;
}

.card {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
