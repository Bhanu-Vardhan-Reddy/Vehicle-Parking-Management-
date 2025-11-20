<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
body {
  background-color: #f8f9fa;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.card {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.status-available {
  background-color: #198754 !important;
  color: white;
}

.status-occupied {
  background-color: #dc3545 !important;
  color: white;
}
</style>

