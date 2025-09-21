<script setup>
import DashboardView from './views/DashboardView.vue'
</script>

<template>
  <nav style="display:flex; gap:2rem; margin-bottom:2rem;">
    <router-link to="/">Usuario</router-link>
    <router-link to="/admin">Administrador</router-link>
  </nav>
  <router-view />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
