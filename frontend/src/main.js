import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Login from './components/Login.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import UserDashboard from './components/UserDashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Login', component: Login },
    { path: '/admin', name: 'AdminDashboard', component: AdminDashboard },
    { path: '/user', name: 'UserDashboard', component: UserDashboard }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  
  if (to.name === 'Login') {
    next()
    return
  }
  
  if (!token) {
    next('/')
    return
  }
  
  if (to.name === 'AdminDashboard' && !user.roles?.includes('admin')) {
    next('/user')
    return
  }
  
  if (to.name === 'UserDashboard' && !user.roles?.includes('user')) {
    next('/admin')
    return
  }
  
  next()
})

const app = createApp(App)
app.use(router)
app.mount('#app')
