import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import DashboardAdmin from '../views/DashboardAdmin.vue'

const routes = [
  { path: '/', name: 'Usuario', component: DashboardView },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
