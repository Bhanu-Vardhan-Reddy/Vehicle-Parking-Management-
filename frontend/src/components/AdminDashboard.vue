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
              <h5 class="card-title">Total Revenue</h5>
              <h2>${{ analyticsStats.total_revenue?.toFixed(2) || '0.00' }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h5 class="card-title">Occupancy Rate</h5>
              <h2>{{ analyticsStats.occupancy_rate || 0 }}%</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-warning text-dark">
            <div class="card-body">
              <h5 class="card-title">Total Bookings</h5>
              <h2>{{ analyticsStats.total_bookings || 0 }}</h2>
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

      <!-- Revenue Chart -->
      <div class="card mb-4">
        <div class="card-header">
          <h4>Revenue by Parking Lot</h4>
        </div>
        <div class="card-body">
          <canvas ref="revenueChart"></canvas>
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

      <!-- All Bookings -->
      <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h4 class="m-0">All Bookings</h4>
          <div class="btn-group" role="group">
            <input 
              type="radio" 
              class="btn-check" 
              id="filterAll" 
              value="" 
              v-model="bookingFilter"
              @change="fetchBookings"
            >
            <label class="btn btn-outline-primary btn-sm" for="filterAll">All</label>
            
            <input 
              type="radio" 
              class="btn-check" 
              id="filterActive" 
              value="Active" 
              v-model="bookingFilter"
              @change="fetchBookings"
            >
            <label class="btn btn-outline-warning btn-sm" for="filterActive">Active</label>
            
            <input 
              type="radio" 
              class="btn-check" 
              id="filterReserved" 
              value="Reserved" 
              v-model="bookingFilter"
              @change="fetchBookings"
            >
            <label class="btn btn-outline-info btn-sm" for="filterReserved">Reserved</label>
            
            <input 
              type="radio" 
              class="btn-check" 
              id="filterCompleted" 
              value="Completed" 
              v-model="bookingFilter"
              @change="fetchBookings"
            >
            <label class="btn btn-outline-success btn-sm" for="filterCompleted">Completed</label>
          </div>
        </div>
        <div class="card-body">
          <div v-if="bookings.length === 0" class="text-center text-muted py-4">
            <p>No bookings found.</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-striped table-hover">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Type</th>
                  <th>Lot</th>
                  <th>Spot</th>
                  <th>Start Time</th>
                  <th>End Time</th>
                  <th>Duration</th>
                  <th>Cost</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="booking in bookings" :key="booking.id">
                  <td>{{ booking.user_email }}</td>
                  <td>
                    <span class="badge bg-secondary">
                      {{ booking.booking_type === 'immediate' ? 'Book' : 'Reserve' }}
                    </span>
                  </td>
                  <td>{{ booking.lot_name }}</td>
                  <td><strong>#{{ booking.spot_number }}</strong></td>
                  <td>{{ formatDateTime(booking.start_time) }}</td>
                  <td>
                    {{ booking.end_time ? formatDateTime(booking.end_time) : 
                       (booking.reserved_end ? formatDateTime(booking.reserved_end) : '-') 
                    }}
                  </td>
                  <td>
                    {{ booking.end_time ? 
                       calculateDuration(booking.start_time, booking.end_time) : 
                       (booking.reserved_start && booking.reserved_end ? 
                        calculateDuration(booking.reserved_start, booking.reserved_end) : 'Ongoing')
                    }}
                  </td>
                  <td><strong>${{ booking.total_cost.toFixed(2) }}</strong></td>
                  <td>
                    <span 
                      class="badge" 
                      :class="{
                        'bg-warning': booking.status === 'Active',
                        'bg-success': booking.status === 'Completed',
                        'bg-info': booking.status === 'Reserved'
                      }"
                    >
                      {{ booking.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
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
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'AdminDashboard',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      token: localStorage.getItem('token'),
      
      lots: [],
      users: [],
      spots: [],
      bookings: [],
      analyticsStats: {},
      selectedLot: null,
      bookingFilter: '',  // '', 'Active', 'Reserved', 'Completed'
      revenueChartInstance: null,
      
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
    this.fetchBookings()
    this.fetchAnalytics()
  },
  
  beforeUnmount() {
    if (this.revenueChartInstance) {
      this.revenueChartInstance.destroy()
    }
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
    
    async fetchBookings() {
      try {
        let url = '/api/admin/bookings'
        if (this.bookingFilter) {
          url += `?status=${this.bookingFilter}`
        }
        
        const response = await axios.get(url, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.bookings = response.data.bookings
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to fetch bookings'
      }
    },
    
    async fetchAnalytics() {
      try {
        const response = await axios.get('/api/stats/admin', {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.analyticsStats = response.data
        
        // Wait for next tick to ensure canvas is rendered
        this.$nextTick(() => {
          this.renderRevenueChart()
        })
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to fetch analytics'
      }
    },
    
    renderRevenueChart() {
      if (!this.$refs.revenueChart) return
      
      // Destroy existing chart
      if (this.revenueChartInstance) {
        this.revenueChartInstance.destroy()
      }
      
      const ctx = this.$refs.revenueChart.getContext('2d')
      const revenueData = this.analyticsStats.revenue_by_lot || []
      
      this.revenueChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: revenueData.map(item => item.lot_name),
          datasets: [{
            label: 'Revenue ($)',
            data: revenueData.map(item => item.revenue),
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: true,
              position: 'top'
            },
            title: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '$' + value.toFixed(2)
                }
              }
            }
          }
        }
      })
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
    
    formatDateTime(isoString) {
      if (!isoString) return '-'
      const date = new Date(isoString)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    calculateDuration(startTime, endTime) {
      const start = new Date(startTime)
      const end = new Date(endTime)
      const diff = end - start
      
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      
      return `${hours}h ${minutes}m`
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
