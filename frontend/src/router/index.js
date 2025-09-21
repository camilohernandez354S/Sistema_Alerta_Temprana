import { createRouter, createWebHistory } from 'vue-router'
import DashboardUsuario from '../views/DashboardUsuario.vue'
import DashboardAdmin from '../views/DashboardAdmin.vue'

const routes = [
  { path: '/', name: 'Usuario', component: DashboardUsuario },
  { path: '/admin', name: 'Admin', component: DashboardAdmin }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
