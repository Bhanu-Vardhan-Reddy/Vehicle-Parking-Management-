<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <h3 class="card-title text-center mb-4">
              🚗 Vehicle Parking System
            </h3>
            <h5 class="text-center mb-4">
              {{ isRegistering ? 'Register' : 'Login' }}
            </h5>
            
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            <div v-if="success" class="alert alert-success" role="alert">
              {{ success }}
            </div>
            
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="form.email" 
                  required
                  placeholder="your@email.com"
                >
              </div>
              
              <div class="mb-3" v-if="isRegistering">
                <label class="form-label">Username</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="form.username"
                  placeholder="Your Name"
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="form.password" 
                  required
                  placeholder="••••••••"
                >
              </div>
              
              <button type="submit" class="btn btn-primary w-100 mb-3">
                {{ isRegistering ? 'Register' : 'Login' }}
              </button>
            </form>
            
            <div class="text-center">
              <button class="btn btn-link" @click="toggleMode">
                {{ isRegistering ? 'Already have an account? Login' : 'Need an account? Register' }}
              </button>
            </div>
            
            <div class="mt-4 p-3 bg-light rounded" v-if="!isRegistering">
              <small class="text-muted">
                <strong>Default Admin:</strong><br>
                Email: nbhanuvardhanreddy@gmail.com<br>
                Password: admin123
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Login',
  data() {
    return {
      isRegistering: false,
      form: {
        email: '',
        password: '',
        username: ''
      },
      error: null,
      success: null
    }
  },
  methods: {
    toggleMode() {
      this.isRegistering = !this.isRegistering
      this.error = null
      this.success = null
    },
    
    async handleSubmit() {
      this.error = null
      this.success = null
      
      try {
        const endpoint = this.isRegistering ? '/auth/register' : '/auth/login'
        const response = await axios.post(endpoint, this.form)
        
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        
        this.success = response.data.message
        
        setTimeout(() => {
          if (response.data.user.roles.includes('admin')) {
            this.$router.push('/admin')
          } else {
            this.$router.push('/user')
          }
        }, 500)
        
      } catch (err) {
        this.error = err.response?.data?.message || 'An error occurred'
      }
    }
  }
}
</script>
