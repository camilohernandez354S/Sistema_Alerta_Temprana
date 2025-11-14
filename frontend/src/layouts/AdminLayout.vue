<template>
  <div class="min-h-screen bg-[#aaaaaa] flex">
    <!-- Botón de menú móvil -->
    <button 
      @click="sidebarOpen = !sidebarOpen"
      class="lg:hidden fixed top-2 left-2 sm:top-4 sm:left-4 z-50 bg-[#005187] text-white p-1.5 sm:p-2 rounded-lg shadow-lg hover:bg-[#4d82bc] transition-colors"
      aria-label="Toggle menu"
    >
      <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path v-if="!sidebarOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    </button>

    <!-- Overlay para móvil -->
    <div 
      v-if="sidebarOpen"
      @click="sidebarOpen = false"
      class="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
    ></div>

    <!-- Sidebar Lateral -->
    <aside 
      :class="[
        'w-64 bg-[#c4dafa] border-r border-[#84b6f4] flex flex-col fixed lg:static inset-y-0 left-0 z-40 transform transition-transform duration-300 ease-in-out',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      ]"
    >
      <!-- Logo y Título -->
      <div class="p-6 border-b border-[#84b6f4]">
        <div class="flex items-center space-x-3 mb-4">
          <div class="w-10 h-10 bg-[#005187] rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-semibold text-[#005187]">SAT</h1>
            <p class="text-xs text-[#4d82bc]">Sistema Alerta</p>
          </div>
        </div>
        <div v-if="saludo" class="text-xs text-[#005187] font-normal bg-[#fcffff] rounded-md px-3 py-2 border border-[#84b6f4]">
          {{ saludo }}
        </div>
      </div>

      <!-- Navegación -->
      <nav class="flex-1 p-4 space-y-1">
        <div class="text-xs font-medium text-[#4d82bc] uppercase tracking-wider mb-4 px-3">Menú Principal</div>
        
        <router-link to="/admin" class="flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-150" :class="$route.path === '/admin' ? 'bg-[#005187] text-white' : 'text-[#005187] hover:bg-[#84b6f4]'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7m-9 2v8m4-8v8m5 0h-6a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2z"></path>
          </svg>
          <span class="font-medium">Dashboard</span>
        </router-link>

        <router-link to="/admin/mediciones" class="flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-150" :class="$route.path === '/admin/mediciones' ? 'bg-[#005187] text-white' : 'text-[#005187] hover:bg-[#84b6f4]'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <span>Mediciones</span>
        </router-link>

        <router-link to="/admin/alertas" class="flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-150" :class="$route.path === '/admin/alertas' ? 'bg-[#005187] text-white' : 'text-[#005187] hover:bg-[#84b6f4]'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
          <span>Alertas</span>
        </router-link>

        <router-link to="/admin/mapas" class="flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-150" :class="$route.path === '/admin/mapas' ? 'bg-[#005187] text-white' : 'text-[#005187] hover:bg-[#84b6f4]'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
          </svg>
          <span>Mapas</span>
        </router-link>

        <router-link to="/admin/configuracion" class="flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-150" :class="$route.path === '/admin/configuracion' ? 'bg-[#005187] text-white' : 'text-[#005187] hover:bg-[#84b6f4]'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
          <span>Configuración</span>
        </router-link>
      </nav>

      <!-- Usuario y Logout -->
      <div class="p-4 border-t border-[#84b6f4] space-y-3">
        <div class="flex items-center space-x-3 px-4 py-3 bg-[#fcffff] rounded-lg border border-[#84b6f4]">
          <div class="w-9 h-9 bg-[#005187] rounded-full flex items-center justify-center">
            <span class="text-white font-medium text-sm">A</span>
          </div>
          <div class="flex-1">
            <div class="text-sm font-medium text-[#005187]">Administrador</div>
            <div class="text-xs text-[#4d82bc]">admin@sistema.local</div>
          </div>
        </div>
        <button @click="handleLogout" class="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-[#4d82bc] text-white rounded-lg hover:bg-[#005187] transition-colors duration-150 font-medium">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
          </svg>
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </aside>

    <!-- Contenido Principal -->
    <div class="flex-1 flex flex-col overflow-hidden bg-[#fcffff] lg:ml-0">
      <!-- Header Superior -->
      <header class="bg-[#fcffff] border-b border-[#c4dafa] pl-11 sm:pl-3 md:pl-6 lg:pl-8 pr-2 sm:pr-4 md:pr-6 lg:pr-8 py-2 sm:py-4 md:py-5">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-3 md:gap-4">
          <div class="min-w-0 flex-1">
            <h1 class="text-lg sm:text-xl md:text-2xl font-semibold text-[#005187] truncate">{{ pageTitle }}</h1>
            <p class="text-xs sm:text-sm text-[#4d82bc] mt-0.5 sm:mt-1 line-clamp-1">{{ pageSubtitle }}</p>
          </div>
          <div class="flex items-center gap-2 sm:gap-3 md:gap-4 w-full sm:w-auto">
            <div class="flex items-center space-x-2 px-2 sm:px-3 py-1.5 bg-[#c4dafa] rounded-full border border-[#84b6f4]">
              <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
              <span class="text-xs sm:text-sm font-medium text-[#005187] hidden sm:inline">Sistema Activo</span>
              <span class="text-xs font-medium text-[#005187] sm:hidden">Activo</span>
            </div>
          </div>
        </div>
      </header>

      <!-- Contenido con Scroll -->
      <main class="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { logout } from '../services/authService'
import { getToken } from '../services/authService'
import { API_URL } from '../config/api.js'

const props = defineProps({
  pageTitle: {
    type: String,
    default: 'Panel de Administrador'
  },
  pageSubtitle: {
    type: String,
    default: 'Sistema de Alerta Temprana - Monitoreo en Tiempo Real'
  }
})

const router = useRouter()
const saludo = ref('')
const sidebarOpen = ref(false)

const handleLogout = () => {
  logout()
  router.push('/login')
}

onMounted(async () => {
  try {
    const resp = await fetch(`${API_URL}/saludo-usuario`, {
      headers: { 'Authorization': 'Bearer ' + getToken() }
    })
    const data = await resp.json()
    if (resp.ok) {
      saludo.value = data.mensaje
    }
  } catch (e) {
    saludo.value = ''
  }
})
</script>

