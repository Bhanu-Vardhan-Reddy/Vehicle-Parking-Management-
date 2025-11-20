<template>
  <div>
    <!-- Navbar -->
    <nav class="navbar navbar-dark bg-primary">
      <div class="container-fluid">
        <span class="navbar-brand">🚗 User Dashboard</span>
        <div class="d-flex align-items-center text-white">
          <span class="me-3">{{ user.email }}</span>
          <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
        </div>
      </div>
    </nav>

    <div class="container-fluid mt-4">
      <h2 class="mb-4">My Parking</h2>
      
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
              <h5 class="card-title">Total Bookings</h5>
              <h2>{{ stats.total }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-warning text-dark">
            <div class="card-body">
              <h5 class="card-title">Active</h5>
              <h2>{{ stats.active }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h5 class="card-title">Completed</h5>
              <h2>{{ stats.completed }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-info text-white">
            <div class="card-body">
              <h5 class="card-title">Total Spent</h5>
              <h2>${{ stats.totalSpent }}</h2>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Booking Card -->
      <div v-if="activeBooking" class="card mb-4 border-warning">
        <div class="card-header bg-warning">
          <h4 class="m-0">🅿️ Active Booking</h4>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <p><strong>Parking Lot:</strong> {{ activeBooking.lot_name }}</p>
              <p><strong>Spot Number:</strong> #{{ activeBooking.spot_number }}</p>
              <p><strong>Start Time:</strong> {{ formatDateTime(activeBooking.start_time) }}</p>
              <p><strong>Price:</strong> ${{ activeBooking.price_per_hour }}/hour</p>
            </div>
            <div class="col-md-6">
              <p><strong>Duration:</strong> {{ calculateDuration(activeBooking.start_time) }}</p>
              <p><strong>Estimated Cost:</strong> ${{ estimateCost(activeBooking) }}</p>
              <button 
                class="btn btn-danger btn-lg w-100 mt-3" 
                @click="confirmRelease"
                :disabled="loading"
              >
                {{ loading ? 'Releasing...' : 'Release Spot' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Book New Spot -->
      <div v-else class="card mb-4">
        <div class="card-header bg-primary text-white">
          <h4 class="m-0">Book a Parking Spot</h4>
        </div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-8">
              <label class="form-label">Select Parking Lot</label>
              <select class="form-select form-select-lg" v-model="selectedLotId">
                <option value="">-- Choose a parking lot --</option>
                <option 
                  v-for="lot in availableLots" 
                  :key="lot.id" 
                  :value="lot.id"
                  :disabled="lot.available_spots === 0"
                >
                  {{ lot.name }} - ${{ lot.price_per_hour }}/hr 
                  ({{ lot.available_spots }} spots available)
                </option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label">&nbsp;</label>
              <button 
                class="btn btn-success btn-lg w-100" 
                @click="bookSpot"
                :disabled="!selectedLotId || loading"
              >
                {{ loading ? 'Booking...' : 'Book Now' }}
              </button>
            </div>
          </div>
          <div v-if="lots.length === 0" class="alert alert-info mt-3">
            No parking lots available. Please check back later.
          </div>
        </div>
      </div>

      <!-- Booking History -->
      <div class="card">
        <div class="card-header">
          <h4>Booking History</h4>
        </div>
        <div class="card-body">
          <div v-if="bookings.length === 0" class="text-center text-muted py-4">
            <p>No bookings yet. Book your first spot above!</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-striped">
              <thead>
                <tr>
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
                  <td>{{ booking.lot_name }}</td>
                  <td>#{{ booking.spot_number }}</td>
                  <td>{{ formatDateTime(booking.start_time) }}</td>
                  <td>
                    {{ booking.end_time ? formatDateTime(booking.end_time) : '-' }}
                  </td>
                  <td>
                    {{ booking.end_time ? 
                       calculateHistoryDuration(booking.start_time, booking.end_time) : 
                       'Ongoing' 
                    }}
                  </td>
                  <td>
                    <strong>${{ booking.total_cost.toFixed(2) }}</strong>
                  </td>
                  <td>
                    <span 
                      class="badge" 
                      :class="booking.status === 'Active' ? 'bg-warning' : 'bg-success'"
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
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserDashboard',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      token: localStorage.getItem('token'),
      
      lots: [],
      bookings: [],
      selectedLotId: '',
      
      error: null,
      success: null,
      loading: false,
      
      currentTime: new Date()
    }
  },
  
  computed: {
    activeBooking() {
      return this.bookings.find(b => b.status === 'Active')
    },
    
    availableLots() {
      return this.lots.filter(lot => lot.available_spots > 0)
    },
    
    stats() {
      return {
        total: this.bookings.length,
        active: this.bookings.filter(b => b.status === 'Active').length,
        completed: this.bookings.filter(b => b.status === 'Completed').length,
        totalSpent: this.bookings
          .filter(b => b.status === 'Completed')
          .reduce((sum, b) => sum + b.total_cost, 0)
          .toFixed(2)
      }
    }
  },
  
  mounted() {
    this.fetchLots()
    this.fetchBookings()
    
    // Update current time every second for duration display
    setInterval(() => {
      this.currentTime = new Date()
    }, 1000)
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
    
    async fetchBookings() {
      try {
        const response = await axios.get('/api/bookings', {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.bookings = response.data.bookings
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to fetch bookings'
      }
    },
    
    async bookSpot() {
      this.error = null
      this.success = null
      this.loading = true
      
      try {
        const response = await axios.post('/api/book', 
          { lot_id: parseInt(this.selectedLotId) },
          { headers: { Authorization: `Bearer ${this.token}` } }
        )
        
        this.success = response.data.message
        this.selectedLotId = ''
        await this.fetchLots()
        await this.fetchBookings()
        
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to book spot'
      } finally {
        this.loading = false
      }
    },
    
    confirmRelease() {
      const cost = this.estimateCost(this.activeBooking)
      if (confirm(`Release this spot?\n\nEstimated Cost: $${cost}\n\nThis cannot be undone.`)) {
        this.releaseSpot()
      }
    },
    
    async releaseSpot() {
      this.error = null
      this.success = null
      this.loading = true
      
      try {
        const response = await axios.post(
          `/api/release/${this.activeBooking.id}`,
          {},
          { headers: { Authorization: `Bearer ${this.token}` } }
        )
        
        this.success = `${response.data.message} - Total Cost: $${response.data.booking.total_cost}`
        await this.fetchLots()
        await this.fetchBookings()
        
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to release spot'
      } finally {
        this.loading = false
      }
    },
    
    formatDateTime(isoString) {
      const date = new Date(isoString)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    calculateDuration(startTime) {
      const start = new Date(startTime)
      const diff = this.currentTime - start
      
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)
      
      return `${hours}h ${minutes}m ${seconds}s`
    },
    
    calculateHistoryDuration(startTime, endTime) {
      const start = new Date(startTime)
      const end = new Date(endTime)
      const diff = end - start
      
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      
      return `${hours}h ${minutes}m`
    },
    
    estimateCost(booking) {
      const start = new Date(booking.start_time)
      const diff = this.currentTime - start
      const hours = Math.max(1, diff / (1000 * 60 * 60)) // Minimum 1 hour
      
      return (hours * booking.price_per_hour).toFixed(2)
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
.card {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.table th {
  background-color: #f8f9fa;
}
</style>
