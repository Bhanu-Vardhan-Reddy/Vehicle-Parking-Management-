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
              <h2>Rs.{{ stats.totalSpent }}</h2>
            </div>
          </div>
        </div>
      </div>

      <!-- Book New Spot -->
      <div class="card mb-4">
        <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
          <h4 class="m-0">Book or Reserve a Parking Spot</h4>
          <div class="btn-group" role="group">
            <input 
              type="radio" 
              class="btn-check" 
              id="bookNow" 
              value="immediate" 
              v-model="bookingType"
              @change="resetForm"
            >
            <label class="btn btn-outline-light btn-sm" for="bookNow">Book Now</label>
            
            <input 
              type="radio" 
              class="btn-check" 
              id="reserve" 
              value="reserved" 
              v-model="bookingType"
              @change="resetForm"
            >
            <label class="btn btn-outline-light btn-sm" for="reserve">Reserve</label>
          </div>
        </div>
        <div class="card-body">
          <!-- Select Parking Lot -->
          <div class="row g-3 mb-3">
            <div class="col-md-12">
              <label class="form-label">Select Parking Lot</label>
              <select 
                class="form-select form-select-lg" 
                v-model="selectedLotId"
                @change="onLotChange"
              >
                <option value="">-- Choose a parking lot --</option>
                <option 
                  v-for="lot in availableLots" 
                  :key="lot.id" 
                  :value="lot.id"
                  :disabled="lot.available_spots === 0 && bookingType === 'immediate'"
                >
                  {{ lot.name }} - Rs.{{ lot.price_per_hour }}/hr 
                  <template v-if="bookingType === 'immediate'">
                    ({{ lot.available_spots }} spots available)
                  </template>
                </option>
              </select>
            </div>
          </div>

          <!-- Reservation Date/Time Inputs -->
          <div v-if="bookingType === 'reserved'" class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label">Start Date & Time</label>
              <input 
                type="datetime-local" 
                class="form-control" 
                v-model="reservedStart"
                :min="minDateTime"
              >
            </div>
            <div class="col-md-6">
              <label class="form-label">End Date & Time</label>
              <input 
                type="datetime-local" 
                class="form-control" 
                v-model="reservedEnd"
                :min="reservedStart || minDateTime"
              >
            </div>
            <div v-if="reservedStart && reservedEnd" class="col-md-12">
              <div class="alert alert-info">
                <strong>Duration:</strong> {{ calculateReservationDuration() }}
                <br>
                <strong>Estimated Cost:</strong> Rs.{{ calculateReservationCost() }}
              </div>
            </div>
          </div>

          <!-- View Spots Toggle -->
          <div v-if="selectedLotId" class="mb-3">
            <button 
              class="btn btn-info w-100" 
              @click="toggleViewSpots"
              :disabled="loading"
            >
              {{ showSpots ? 'Hide Spots' : 'View & Select Spot' }}
            </button>
          </div>

          <!-- Spots Grid -->
          <div v-if="showSpots && spots.length > 0" class="mb-3">
            <div class="card">
              <div class="card-header">
                <h5 class="m-0">
                  {{ selectedSpot ? `Selected: Spot #${selectedSpot.spot_number}` : 'Select a Spot (or leave blank for auto-assign)' }}
                </h5>
              </div>
              <div class="card-body">
                <div class="row g-2">
                  <div 
                    class="col-6 col-md-3 col-lg-2" 
                    v-for="spot in spots" 
                    :key="spot.id"
                  >
                    <div 
                      class="card text-center py-3 spot-card"
                      :class="{
                        'status-available': canSelectSpot(spot),
                        'status-occupied': !canSelectSpot(spot),
                        'spot-selected': selectedSpot && selectedSpot.id === spot.id
                      }"
                      @click="selectSpot(spot)"
                      :style="canSelectSpot(spot) ? 'cursor: pointer;' : 'cursor: not-allowed;'"
                    >
                      <strong>Spot #{{ spot.spot_number }}</strong>
                      <small v-if="spot.status === 'Occupied'">Occupied</small>
                      <small v-else-if="spot.reservations.length > 0 && bookingType === 'reserved'">
                        Reserved
                      </small>
                      <small v-else>Available</small>
                      
                      <!-- Show reservations for this spot -->
                      <div v-if="spot.reservations.length > 0 && bookingType === 'reserved'" class="mt-1">
                        <small class="d-block text-white" v-for="(res, idx) in spot.reservations" :key="idx" style="font-size: 0.7rem;">
                          {{ formatShortDateTime(res.start) }} - {{ formatShortDateTime(res.end) }}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mt-2">
                  <button 
                    v-if="selectedSpot" 
                    class="btn btn-secondary btn-sm" 
                    @click="clearSpotSelection"
                  >
                    Clear Selection (Auto-assign)
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Book/Reserve Button -->
          <div class="row">
            <div class="col-md-12">
              <button 
                class="btn btn-success btn-lg w-100" 
                @click="submitBooking"
                :disabled="!canSubmit || loading"
              >
                {{ loading ? 'Processing...' : (bookingType === 'immediate' ? 'Book Now' : 'Reserve Spot') }}
              </button>
            </div>
          </div>

          <div v-if="lots.length === 0" class="alert alert-info mt-3">
            No parking lots available. Please check back later.
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
              <p><strong>Price:</strong> Rs.{{ activeBooking.price_per_hour }}/hour</p>
            </div>
            <div class="col-md-6">
              <p><strong>Duration:</strong> {{ calculateDuration(activeBooking.start_time) }}</p>
              <p><strong>Estimated Cost:</strong> Rs.{{ estimateCost(activeBooking) }}</p>
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

      <!-- Analytics Chart -->
      <div class="card mb-4">
        <div class="card-header">
          <h4>Monthly Booking Activity (Last 6 Months)</h4>
        </div>
        <div class="card-body">
          <canvas ref="monthlyChart"></canvas>
        </div>
      </div>

      <!-- Booking History -->
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h4 class="m-0">Booking History</h4>
          <button 
            class="btn btn-success btn-sm" 
            @click="exportBookings"
            :disabled="loading || bookings.length === 0"
          >
            📄 Export CSV
          </button>
        </div>
        <div class="card-body">
          <div v-if="bookings.length === 0" class="text-center text-muted py-4">
            <p>No bookings yet. Book your first spot above!</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-striped">
              <thead>
                <tr>
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
                  <td>
                    <span class="badge bg-secondary">
                      {{ booking.booking_type === 'immediate' ? 'Book' : 'Reserve' }}
                    </span>
                  </td>
                  <td>{{ booking.lot_name }}</td>
                  <td>#{{ booking.spot_number }}</td>
                  <td>{{ formatDateTime(booking.start_time) }}</td>
                  <td>
                    {{ booking.end_time ? formatDateTime(booking.end_time) : 
                       (booking.reserved_end ? formatDateTime(booking.reserved_end) : '-') 
                    }}
                  </td>
                  <td>
                    {{ booking.end_time ? 
                       calculateHistoryDuration(booking.start_time, booking.end_time) : 
                       (booking.reserved_start && booking.reserved_end ? 
                        calculateHistoryDuration(booking.reserved_start, booking.reserved_end) : 'Ongoing')
                    }}
                  </td>
                  <td>
                    <strong>Rs.{{ booking.total_cost.toFixed(2) }}</strong>
                  </td>
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
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'UserDashboard',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      token: localStorage.getItem('token'),
      
      lots: [],
      bookings: [],
      spots: [],
      userStats: {},
      
      bookingType: 'immediate',
      selectedLotId: '',
      selectedSpot: null,
      showSpots: false,
      monthlyChartInstance: null,
      
      reservedStart: '',
      reservedEnd: '',
      
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
      if (this.bookingType === 'immediate') {
        return this.lots.filter(lot => lot.available_spots > 0)
      }
      return this.lots
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
    },
    
    minDateTime() {
      const now = new Date()
      return now.toISOString().slice(0, 16)
    },
    
    canSubmit() {
      if (!this.selectedLotId) return false
      if (this.bookingType === 'reserved') {
        return this.reservedStart && this.reservedEnd
      }
      return true
    },
    
    selectedLot() {
      return this.lots.find(l => l.id === parseInt(this.selectedLotId))
    }
  },
  
  mounted() {
    this.fetchLots()
    this.fetchBookings()
    this.fetchUserStats()
    
    setInterval(() => {
      this.currentTime = new Date()
    }, 1000)
  },
  
  beforeUnmount() {
    if (this.monthlyChartInstance) {
      this.monthlyChartInstance.destroy()
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
    
    async fetchUserStats() {
      try {
        const response = await axios.get('/api/stats/user', {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.userStats = response.data
        
        this.$nextTick(() => {
          this.renderMonthlyChart()
        })
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to fetch statistics'
      }
    },
    
    renderMonthlyChart() {
      if (!this.$refs.monthlyChart) return
      
      if (this.monthlyChartInstance) {
        this.monthlyChartInstance.destroy()
      }
      
      const ctx = this.$refs.monthlyChart.getContext('2d')
      const monthlyData = this.userStats.monthly_bookings || []
      
      this.monthlyChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: monthlyData.map(item => item.month),
          datasets: [
            {
              label: 'Bookings',
              data: monthlyData.map(item => item.bookings),
              borderColor: 'rgba(75, 192, 192, 1)',
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderWidth: 2,
              tension: 0.4,
              yAxisID: 'y'
            },
            {
              label: 'Spending (Rs.)',
              data: monthlyData.map(item => item.spending),
              borderColor: 'rgba(255, 99, 132, 1)',
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              borderWidth: 2,
              tension: 0.4,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          interaction: {
            mode: 'index',
            intersect: false
          },
          plugins: {
            legend: {
              display: true,
              position: 'top'
            }
          },
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              beginAtZero: true,
              ticks: {
                precision: 0,
                stepSize: 1
              },
              title: {
                display: true,
                text: 'Number of Bookings'
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              beginAtZero: true,
              suggestedMax: Math.max(...monthlyData.map(item => item.spending || 0), 10) * 1.2,
              grid: {
                drawOnChartArea: false
              },
              title: {
                display: true,
                text: 'Spending (Rs.)'
              },
              ticks: {
                callback: function(value) {
                  return 'Rs.' + value.toFixed(0)
                }
              }
            }
          }
        }
      })
    },
    
    async fetchSpots() {
      if (!this.selectedLotId) return
      
      this.loading = true
      try {
        const response = await axios.get(`/api/spots/${this.selectedLotId}`, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.spots = response.data.spots
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to fetch spots'
      } finally {
        this.loading = false
      }
    },
    
    onLotChange() {
      this.showSpots = false
      this.selectedSpot = null
      this.spots = []
    },
    
    async toggleViewSpots() {
      this.showSpots = !this.showSpots
      if (this.showSpots && this.spots.length === 0) {
        await this.fetchSpots()
      }
    },
    
    canSelectSpot(spot) {
      if (this.bookingType === 'immediate') {
        return spot.status === 'Available'
      } else {
        if (!this.reservedStart || !this.reservedEnd) return true
        
        return spot.reservations.length === 0 || !this.hasTimeConflict(spot)
      }
    },
    
    hasTimeConflict(spot) {
      if (!this.reservedStart || !this.reservedEnd) return false
      
      const reqStart = new Date(this.reservedStart)
      const reqEnd = new Date(this.reservedEnd)
      
      return spot.reservations.some(res => {
        const resStart = new Date(res.start)
        const resEnd = new Date(res.end)
        
        return (
          (reqStart >= resStart && reqStart < resEnd) ||
          (reqEnd > resStart && reqEnd <= resEnd) ||
          (reqStart <= resStart && reqEnd >= resEnd)
        )
      })
    },
    
    selectSpot(spot) {
      if (!this.canSelectSpot(spot)) {
        this.error = `Spot #${spot.spot_number} is not available for the selected time`
        return
      }
      
      if (this.selectedSpot && this.selectedSpot.id === spot.id) {
        this.selectedSpot = null
      } else {
        this.selectedSpot = spot
        this.error = null
      }
    },
    
    clearSpotSelection() {
      this.selectedSpot = null
    },
    
    resetForm() {
      this.selectedLotId = ''
      this.selectedSpot = null
      this.showSpots = false
      this.spots = []
      this.reservedStart = ''
      this.reservedEnd = ''
      this.error = null
    },
    
    async submitBooking() {
      this.error = null
      this.success = null
      this.loading = true
      
      const payload = {
        lot_id: parseInt(this.selectedLotId),
        booking_type: this.bookingType
      }
      
      if (this.selectedSpot) {
        payload.spot_id = this.selectedSpot.id
      }
      
      if (this.bookingType === 'reserved') {
        payload.reserved_start = new Date(this.reservedStart).toISOString()
        payload.reserved_end = new Date(this.reservedEnd).toISOString()
      }
      
      try {
        const response = await axios.post('/api/book', payload, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        
        this.success = response.data.message
        this.resetForm()
        await this.fetchLots()
        await this.fetchBookings()
        
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to complete booking'
        
        if (err.response?.data?.conflict) {
          const conflict = err.response.data.conflict
          this.error += ` (Conflict: ${this.formatDateTime(conflict.start)} - ${this.formatDateTime(conflict.end)})`
        }
      } finally {
        this.loading = false
      }
    },
    
    confirmRelease() {
      const cost = this.estimateCost(this.activeBooking)
      if (confirm(`Release this spot?\n\nEstimated Cost: Rs.${cost}\n\nThis cannot be undone.`)) {
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
        
        this.success = `${response.data.message} - Total Cost: Rs.${response.data.booking.total_cost}`
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
    
    formatShortDateTime(isoString) {
      const date = new Date(isoString)
      return date.toLocaleString('en-US', {
        month: 'numeric',
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
    
    calculateReservationDuration() {
      if (!this.reservedStart || !this.reservedEnd) return 'N/A'
      
      const start = new Date(this.reservedStart)
      const end = new Date(this.reservedEnd)
      const diff = end - start
      
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      
      return `${hours}h ${minutes}m`
    },
    
    calculateReservationCost() {
      if (!this.reservedStart || !this.reservedEnd || !this.selectedLot) return '0.00'
      
      const start = new Date(this.reservedStart)
      const end = new Date(this.reservedEnd)
      const hours = Math.max(1, (end - start) / (1000 * 60 * 60))
      
      return (hours * this.selectedLot.price_per_hour).toFixed(2)
    },
    
    estimateCost(booking) {
      const start = new Date(booking.start_time)
      const diff = this.currentTime - start
      const hours = Math.max(1, diff / (1000 * 60 * 60))
      
      return (hours * booking.price_per_hour).toFixed(2)
    },
    
    async exportBookings() {
      this.error = null
      this.success = null
      this.loading = true
      
      try {
        const response = await axios.get('/api/export', {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        
        this.success = '📧 CSV export started! You will receive an email with your booking history shortly. Check your inbox!'
        if (response.data.task_id) {
          this.success += ` (Task ID: ${response.data.task_id})`
        }
        
        this.fetchBookings()
        
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to export bookings. Please try again.'
      } finally {
        this.loading = false
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
.card {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.table th {
  background-color: #f8f9fa;
}

.spot-card {
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.status-available {
  background-color: #198754;
  color: white;
}

.status-occupied {
  background-color: #dc3545;
  color: white;
  opacity: 0.6;
}

.spot-selected {
  border: 3px solid #ffc107 !important;
  box-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
  transform: scale(1.05);
}

.spot-card:hover {
  transform: scale(1.05);
}
</style>
