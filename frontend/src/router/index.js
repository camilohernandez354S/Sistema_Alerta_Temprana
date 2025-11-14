import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import DashboardAdmin from '../views/DashboardAdmin.vue'
import DashboardUsuario from '../views/DashboardUsuario.vue'
import Login from '../views/Login.vue'
import MedicionesView from '../views/MedicionesView.vue'
import AlertasView from '../views/AlertasView.vue'
import MapasView from '../views/MapasView.vue'
import ConfiguracionView from '../views/ConfiguracionView.vue'
import { getToken, getRol } from '../services/authService'

const routes = [
  { path: '/login', name: 'Login', component: Login },
  { path: '/admin', name: 'Admin', component: DashboardAdmin, meta: { requiresAuth: true, rol: 'admin' } },
  { path: '/admin/mediciones', name: 'Mediciones', component: MedicionesView, meta: { requiresAuth: true, rol: 'admin' } },
  { path: '/admin/alertas', name: 'Alertas', component: AlertasView, meta: { requiresAuth: true, rol: 'admin' } },
  { path: '/admin/mapas', name: 'Mapas', component: MapasView, meta: { requiresAuth: true, rol: 'admin' } },
  { path: '/admin/configuracion', name: 'Configuracion', component: ConfiguracionView, meta: { requiresAuth: true, rol: 'admin' } },
  { path: '/usuario', name: 'Usuario', component: DashboardView, meta: { requiresAuth: true, rol: 'usuario' } },
  { path: '/', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = getToken()
    const rol = getRol()
    if (!token) {
      next('/login')
    } else if (to.meta.rol && to.meta.rol !== rol) {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
