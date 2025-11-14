<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50" 
       :class="alertClass">
    <!-- Encabezado mejorado -->
    <header class="bg-white/80 backdrop-blur-sm shadow-lg border-b border-blue-200/50 px-6 py-6">
      <div class="max-w-7xl mx-auto">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <div>
                <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Sistema de Alerta Temprana
                </h1>
                <p class="text-sm text-gray-600 mt-1 flex items-center space-x-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                  <span>{{ fechaActual }}</span>
                </p>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <!-- Indicador de alerta -->
            <div v-if="isFloodAlert || isDroughtAlert" class="flex items-center space-x-3 bg-white/80 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg border-2 border-white/50">
              <div class="flex items-center space-x-2">
                <div class="w-4 h-4 rounded-full alert-indicator animate-pulse"></div>
                <span class="text-sm font-bold" :class="isFloodAlert ? 'text-red-700' : 'text-orange-700'">
                  {{ isFloodAlert ? '⚠️ INUNDACIÓN' : '⚠️ SEQUÍA' }}
                </span>
              </div>
            </div>
            
            <!-- Indicador de conexión -->
            <div class="flex items-center space-x-3 bg-white/60 backdrop-blur-sm rounded-full px-4 py-2 shadow-sm border border-gray-200/50">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 rounded-full animate-pulse" :class="connectionStatus ? 'bg-emerald-500' : 'bg-red-500'"></div>
                <span class="text-sm font-medium" :class="connectionStatus ? 'text-emerald-700' : 'text-red-700'">
                  {{ connectionStatus ? 'Sensor Activo' : 'Sensor Inactivo' }}
                </span>
              </div>
            </div>
            <button @click="handleLogout" class="bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-2.5 rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 font-medium">
              Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Contenido principal -->
    <main class="max-w-7xl mx-auto px-6 py-8">
      <!-- Estado de carga global mejorado -->
      <div v-if="isLoading" class="flex flex-col justify-center items-center h-64 space-y-4">
        <div class="relative">
          <div class="animate-spin rounded-full h-16 w-16 border-4 border-blue-200"></div>
          <div class="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent absolute top-0 left-0"></div>
        </div>
        <div class="text-center">
          <p class="text-lg font-medium text-gray-700">Cargando datos del sensor...</p>
          <p class="text-sm text-gray-500 mt-1">Conectando con el sistema de monitoreo</p>
        </div>
      </div>

      <!-- Estado de error/información global -->
      <div v-else-if="error" :class="[
        'rounded-lg p-4 mb-6',
        error.includes('demostración') ? 'bg-blue-50 border border-blue-200' : 'bg-red-50 border border-red-200'
      ]">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg v-if="error.includes('demostración')" class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <svg v-else class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium" :class="error.includes('demostración') ? 'text-blue-800' : 'text-red-800'">
              {{ error.includes('demostración') ? 'Modo Demostración' : 'Error al cargar datos' }}
            </h3>
            <p class="mt-1 text-sm" :class="error.includes('demostración') ? 'text-blue-700' : 'text-red-700'">
              {{ error }}
            </p>
            <div class="mt-3 flex space-x-3">
              <button @click="loadData" class="text-sm underline hover:no-underline" 
                      :class="error.includes('demostración') ? 'text-blue-800 hover:text-blue-900' : 'text-red-800 hover:text-red-900'">
                {{ error.includes('demostración') ? 'Intentar conectar con API' : 'Reintentar' }}
              </button>
              <button v-if="!connectionStatus" @click="insertarDatosPrueba" 
                      class="text-sm underline hover:no-underline text-green-800 hover:text-green-900"
                      :disabled="insertandoDatos">
                {{ insertandoDatos ? 'Insertando...' : 'Insertar datos de prueba' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Dashboard principal -->
      <div v-else class="space-y-8">
        <!-- Estado actual y predicciones -->
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <!-- Semáforo de Estado -->
          <div class="lg:col-span-1">
            <Semaforo 
              :estado="currentState.estado"
              :nivel="currentState.nivel_cm"
              :ultima-actualizacion="lastUpdateTime"
            />
          </div>
          
          <!-- Estado actual - Card grande mejorada -->
          <div class="lg:col-span-1">
            <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transition-all duration-300">
              <div class="text-center">
                <div class="flex items-center justify-center mb-6">
                  <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V1a1 1 0 011 1v18a1 1 0 01-1 1H6a1 1 0 01-1-1V2a1 1 0 011-1h8z"></path>
                    </svg>
                  </div>
                </div>
                <h3 class="text-lg font-semibold text-gray-800 mb-6">Estado Actual</h3>
                
                <!-- Nivel actual en texto grande -->
                <div class="mb-6">
                  <div class="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    {{ currentState.nivel_cm || 'N/A' }}
                  </div>
                  <div class="text-sm text-gray-500 font-medium">centímetros</div>
                </div>
                
                <!-- Estado textual -->
                <div class="mb-4">
                  <span class="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold shadow-sm" 
                        :class="getStateColorClass(currentState.estado)">
                    <div class="w-2 h-2 rounded-full mr-2" :class="getStateDotColor(currentState.estado)"></div>
                    {{ currentState.estado || 'Sin datos' }}
                  </span>
                </div>
                
                <!-- Tendencia -->
                <div class="flex items-center justify-center space-x-2 mb-3">
                  <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                    <svg class="w-4 h-4" :class="getTrendIconColor(currentState.tendencia)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getTrendIcon(currentState.tendencia)"></path>
                    </svg>
                  </div>
                  <span class="text-sm font-medium text-gray-700">{{ getTrendText(currentState.tendencia) }}</span>
                </div>
                
                <!-- Pendiente si está disponible -->
                <div v-if="currentState.pendiente_cm_por_h !== undefined" class="text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2">
                  {{ currentState.pendiente_cm_por_h > 0 ? '+' : '' }}{{ currentState.pendiente_cm_por_h?.toFixed(1) }} cm/h
                </div>
                
                <!-- Indicador de WebSocket -->
                <div class="mt-4 flex items-center justify-center space-x-2">
                  <div class="w-2 h-2 rounded-full" :class="wsConnected ? 'bg-green-500' : 'bg-red-500'"></div>
                  <span class="text-xs text-gray-500">{{ wsConnected ? 'Tiempo real activo' : 'Desconectado' }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Predicciones futuras - Tarjetas pequeñas mejoradas -->
          <div class="lg:col-span-3">
            <div class="mb-4">
              <h3 class="text-xl font-bold text-gray-800 mb-2">Predicciones Futuras</h3>
              <p class="text-sm text-gray-600">Análisis predictivo basado en tendencias históricas</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              <div v-for="prediction in predictions" :key="prediction.horizon_min" 
                   class="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-white/30 p-6 hover:shadow-xl hover:bg-white/80 transition-all duration-300 group">
                <div class="text-center">
                  <!-- Icono de tiempo -->
                  <div class="flex justify-center mb-4">
                    <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-md group-hover:scale-110 transition-transform duration-200">
                      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                  </div>
                  
                  <!-- Horizonte temporal -->
                  <div class="text-sm font-semibold text-gray-700 mb-3">
                    {{ formatHorizon(prediction.horizon_min) }}
                  </div>
                  
                  <!-- Nivel predicho -->
                  <div class="text-3xl font-bold text-gray-800 mb-3">
                    {{ prediction.nivel_cm?.toFixed(1) || 'N/A' }}
                  </div>
                  <div class="text-xs text-gray-500 mb-4">cm</div>
                  
                  <!-- Estado y confianza -->
                  <div class="space-y-3">
                    <div>
                      <span class="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold shadow-sm" 
                            :class="getStateColorClass(prediction.estado)">
                        <div class="w-2 h-2 rounded-full mr-2" :class="getStateDotColor(prediction.estado)"></div>
                        {{ prediction.estado || 'Sin datos' }}
                      </span>
                    </div>
                    <div class="bg-gray-50 rounded-lg px-3 py-2">
                      <div class="flex items-center justify-between">
                        <span class="text-xs text-gray-600 font-medium">Confianza</span>
                        <span class="text-xs font-bold text-gray-800">{{ Math.round((prediction.confianza || 0) * 100) }}%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                        <div class="bg-gradient-to-r from-blue-500 to-purple-500 h-1.5 rounded-full transition-all duration-500" 
                             :style="{ width: (prediction.confianza || 0) * 100 + '%' }"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Gráfico principal con datos históricos y predicciones mejorado -->
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transition-all duration-300">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-2xl font-bold text-gray-900 mb-2">Análisis Temporal</h3>
              <p class="text-sm text-gray-600">Evolución del nivel de agua y predicciones futuras</p>
            </div>
            <div class="flex items-center space-x-6 text-sm">
              <div class="flex items-center space-x-3 bg-blue-50 rounded-full px-4 py-2">
                <div class="w-3 h-3 bg-blue-600 rounded-full shadow-sm"></div>
                <span class="font-medium text-blue-800">Datos Históricos</span>
              </div>
              <div class="flex items-center space-x-3 bg-purple-50 rounded-full px-4 py-2">
                <div class="w-3 h-3 bg-purple-500 rounded-full shadow-sm"></div>
                <span class="font-medium text-purple-800">Predicciones</span>
              </div>
            </div>
          </div>
          <div class="h-96 bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl p-4">
            <Line
              v-if="combinedChartData.labels.length > 0"
              :data="combinedChartData"
              :options="chartOptions"
            />
            <div v-else class="flex flex-col items-center justify-center h-full text-gray-500">
              <svg class="w-16 h-16 mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              <p class="text-lg font-medium">No hay datos disponibles</p>
              <p class="text-sm">Conecta el sensor para ver el análisis temporal</p>
            </div>
          </div>
        </div>

        <!-- Mapa de alertas geoespaciales -->
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transition-all duration-300">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-2xl font-bold text-gray-900 mb-2">Mapa de Alertas</h3>
              <p class="text-sm text-gray-600">Visualiza alertas en tiempo real por proximidad geográfica</p>
            </div>
            <div class="flex items-center space-x-2 text-sm text-gray-500">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              <span>Haz clic en el mapa para buscar alertas</span>
            </div>
          </div>
          <GeospatialMap 
            :initial-lat="-34.6037" 
            :initial-lng="-58.3816" 
            :initial-zoom="13"
          />
        </div>

        <!-- Métricas adicionales mejoradas -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Última actualización -->
          <div class="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-white/30 p-6 hover:shadow-xl hover:bg-white/80 transition-all duration-300">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-sm font-semibold text-gray-700 mb-1">Última Actualización</h3>
                <p class="text-xl font-bold text-gray-900 mb-1">{{ lastUpdateTime }}</p>
                <p class="text-xs text-gray-500">Datos del sensor</p>
              </div>
            </div>
          </div>

          <!-- Estado del sistema -->
          <div class="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-white/30 p-6 hover:shadow-xl hover:bg-white/80 transition-all duration-300">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg" :class="statusColor">
                  <svg class="w-7 h-7" :class="statusIconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="statusIcon"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-sm font-semibold text-gray-700 mb-1">Estado del Sistema</h3>
                <p class="text-xl font-bold text-gray-900 mb-1">{{ systemStatus }}</p>
                <p class="text-xs font-medium" :class="statusTextColor">{{ systemStatusDescription }}</p>
              </div>
            </div>
          </div>

          <!-- Datos de predicción -->
          <div class="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-white/30 p-6 hover:shadow-xl hover:bg-white/80 transition-all duration-300">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-sm font-semibold text-gray-700 mb-1">Predicciones</h3>
                <p class="text-xl font-bold text-gray-900 mb-1">{{ predictions.length }}</p>
                <p class="text-xs text-gray-500">Horizontes disponibles</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'
import AlertsPanel from '../components/dashboard/AlertsPanel.vue'
import GeospatialMap from '../components/GeospatialMap.vue'
import Semaforo from '../components/Semaforo.vue'
import { io } from 'socket.io-client'
import { logout } from '../services/authService'
import { useRouter } from 'vue-router'
const router = useRouter()
function handleLogout() {
  logout()
  router.push('/login')
}

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// Estados reactivos
const isLoading = ref(true)
const error = ref(null)
const connectionStatus = ref(false)
const insertandoDatos = ref(false)

// Datos de la API
const waterLevels = ref([])
const predictions = ref([])
const currentState = ref({})

// Variables para alertas visuales
const isFloodAlert = ref(false)
const isDroughtAlert = ref(false)
const alertClass = ref('')

// Intervalo para actualización automática
let refreshInterval = null

// WebSocket connection
let socket = null
const wsConnected = ref(false)

// Fecha actual
const fechaActual = computed(() => {
  return new Date().toLocaleDateString('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

/**
 * Función para formatear fecha
 */
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Función para formatear tiempo
 */
const formatTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Función para formatear horizonte temporal
 */
const formatHorizon = (minutes) => {
  if (minutes < 60) {
    return `${minutes} min`
  } else if (minutes < 1440) { // menos de 24 horas
    const hours = Math.floor(minutes / 60)
    return `${hours}h`
  } else {
    const days = Math.floor(minutes / 1440)
    return `${days}d`
  }
}

/**
 * Obtener clase CSS para el color del estado
 */
const getStateColorClass = (estado) => {
  switch (estado) {
    case 'Sequía':
      return 'bg-orange-100 text-orange-800'
    case 'Inundación':
      return 'bg-red-100 text-red-800'
    case 'Normal':
    default:
      return 'bg-green-100 text-green-800'
  }
}

/**
 * Obtener clase CSS para el color del punto del estado
 */
const getStateDotColor = (estado) => {
  switch (estado) {
    case 'Sequía':
      return 'bg-orange-500'
    case 'Inundación':
      return 'bg-red-500'
    case 'Normal':
    default:
      return 'bg-green-500'
  }
}

/**
 * Función para verificar si hay alerta de inundación
 */
const checkFloodAlert = (estado) => {
  return estado === 'Inundación'
}

/**
 * Función para verificar si hay alerta de sequía
 */
const checkDroughtAlert = (estado) => {
  return estado === 'Sequía'
}

/**
 * Función para actualizar las alertas visuales
 */
const updateAlertStatus = () => {
  const estado = currentState.value.estado
  
  if (estado) {
    isFloodAlert.value = checkFloodAlert(estado)
    isDroughtAlert.value = checkDroughtAlert(estado)
    
    // Actualizar clase de alerta
    if (isFloodAlert.value) {
      alertClass.value = 'flood-alert'
    } else if (isDroughtAlert.value) {
      alertClass.value = 'drought-alert'
    } else {
      alertClass.value = ''
    }
  } else {
    isFloodAlert.value = false
    isDroughtAlert.value = false
    alertClass.value = ''
  }
}

/**
 * Obtener color del icono de tendencia
 */
const getTrendIconColor = (tendencia) => {
  switch (tendencia) {
    case 'sube':
      return 'text-green-600'
    case 'baja':
      return 'text-red-600'
    case 'estable':
    default:
      return 'text-gray-600'
  }
}

/**
 * Obtener texto de tendencia
 */
const getTrendText = (tendencia) => {
  switch (tendencia) {
    case 'sube':
      return 'Subiendo'
    case 'baja':
      return 'Bajando'
    case 'estable':
    default:
      return 'Estable'
  }
}

/**
 * Obtener icono SVG de tendencia
 */
const getTrendIcon = (tendencia) => {
  switch (tendencia) {
    case 'sube':
      return 'M7 14l3-3 3 3'
    case 'baja':
      return 'M17 10l-3 3-3-3'
    case 'estable':
    default:
      return 'M5 12h14'
  }
}

// Datos hardcodeados como fallback
const fallbackWaterLevels = [
  { level: 25.5, timestamp: new Date(Date.now() - 60000 * 60).toISOString() },
  { level: 27.2, timestamp: new Date(Date.now() - 60000 * 50).toISOString() },
  { level: 28.8, timestamp: new Date(Date.now() - 60000 * 40).toISOString() },
  { level: 30.1, timestamp: new Date(Date.now() - 60000 * 30).toISOString() },
  { level: 32.4, timestamp: new Date(Date.now() - 60000 * 20).toISOString() },
  { level: 31.7, timestamp: new Date(Date.now() - 60000 * 10).toISOString() },
  { level: 33.2, timestamp: new Date().toISOString() }
]

// Datos de fallback para predicciones según el formato del nuevo endpoint
const fallbackPredictions = {
  current: { 
    nivel_cm: 42, 
    estado: "Normal", 
    tendencia: "estable", 
    pendiente_cm_por_h: 0.0 
  },
  predicciones: [
    { horizon_min: 30, nivel_cm: 43, estado: "Normal", confianza: 0.7 },
    { horizon_min: 60, nivel_cm: 44, estado: "Normal", confianza: 0.6 },
    { horizon_min: 180, nivel_cm: 47, estado: "Normal", confianza: 0.5 }
  ]
}

/**
 * Función para obtener niveles de agua desde la API
 * Maneja la transformación de datos del backend al formato esperado por el frontend
 */
const fetchWaterLevels = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/mediciones')
    
    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status}`)
    }

    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text()
      throw new Error("Respuesta no es JSON válido. Respuesta recibida: " + text.slice(0, 100))
    }

    const data = await response.json()
    
    // Transformar los datos del backend al formato esperado por el frontend
    // El backend devuelve un array de: { _id, distancia, fecha }
    // El frontend espera: { level, timestamp }
    if (Array.isArray(data)) {
      return data.map(item => ({
        level: item.distancia || item.nivel_agua,
        timestamp: item.fecha || item.timestamp
      }))
    } else if (data.lecturas && Array.isArray(data.lecturas)) {
      return data.lecturas.map(item => ({
        level: item.distancia || item.nivel_agua || item.nivel_cm,
        timestamp: item.fecha || item.timestamp
      }))
    } else if (data.data && Array.isArray(data.data)) {
      return data.data.map(item => ({
        level: item.distancia || item.nivel_agua || item.nivel_cm,
        timestamp: item.fecha || item.timestamp
      }))
    }
    
    return []
  } catch (error) {
    console.error("Error al obtener niveles de agua:", error)
    
    // Si es un error de red o API no disponible, usar datos de fallback
    if (error.message.includes('fetch') || error.message.includes('HTTP') || error.message.includes('Failed to fetch')) {
      console.warn("API no disponible, usando datos de demostración")
      return fallbackWaterLevels
    }
    
    throw error
  }
}

/**
 * Función para obtener predicciones desde el nuevo endpoint Flask
 * Consume el endpoint /api/sensor/predicciones y maneja el formato de respuesta
 * Si la API falla, usa datos de fallback hardcodeados
 */
const fetchPredictions = async () => {
  try {
    console.log("🔍 Iniciando fetch de predicciones...")
    const response = await fetch('http://localhost:5000/api/sensor/predicciones')
    
    console.log("📡 Respuesta recibida:", {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries())
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error("❌ Error HTTP en predicciones:", {
        status: response.status,
        statusText: response.statusText,
        body: errorText
      })
      throw new Error(`Error HTTP: ${response.status} - ${errorText}`)
    }

    const contentType = response.headers.get("content-type")
    console.log("📋 Content-Type:", contentType)
    
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text()
      console.error("❌ Respuesta no es JSON válido:", text.slice(0, 200))
      throw new Error("Respuesta no es JSON válido. Respuesta recibida: " + text.slice(0, 100))
    }

    const data = await response.json()
    console.log("✅ Predicciones recibidas:", data)
    
    // Verificar si hay error en la respuesta
    if (data.error) {
      console.error("❌ Error en respuesta de predicciones:", data.error)
      throw new Error(data.error.message || 'Error en predicciones')
    }
    
    // El endpoint devuelve: { meta, current, predicciones }
    // Devolver en el formato esperado
    const result = {
      meta: data.meta || {},
      current: data.current || {},
      predicciones: data.predicciones || []
    }
    
    console.log("✅ Predicciones procesadas:", {
      meta: result.meta,
      current: result.current,
      prediccionesCount: result.predicciones.length,
      predicciones: result.predicciones
    })
    
    return result
    
  } catch (error) {
    console.error("❌ Error al obtener predicciones:", error)
    
    // Si es un error de red o API no disponible, usar datos de fallback
    if (error.message.includes('fetch') || error.message.includes('HTTP') || error.message.includes('Failed to fetch')) {
      console.warn("⚠️ API de predicciones no disponible, usando datos de demostración")
      return fallbackPredictions
    }
    
    // Para otros errores, también usar fallback
    console.warn("⚠️ Error en predicciones, usando datos de fallback:", error.message)
    return fallbackPredictions
  }
}

/**
 * Función para insertar datos de prueba
 */
const insertarDatosPrueba = async () => {
  try {
    insertandoDatos.value = true
    
    const response = await fetch('http://localhost:5000/api/sensor/datos-prueba', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status}`)
    }
    
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text()
      throw new Error("Respuesta no es JSON válido: " + text.slice(0, 100))
    }
    
    const result = await response.json()
    console.log('Datos de prueba insertados:', result)
    
    // Recargar datos después de insertar
    setTimeout(() => {
      loadData()
    }, 1000)
    
  } catch (err) {
    console.error('Error insertando datos de prueba:', err)
    error.value = `Error insertando datos de prueba: ${err.message}`
  } finally {
    insertandoDatos.value = false
  }
}

/**
 * Función para verificar el estado de conexión del Arduino
 */
const fetchConnectionStatus = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/sensor/estado-conexion')
    
    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status}`)
    }
    
    const data = await response.json()
    console.log("🔌 Estado de conexión Arduino:", data)
    return data
    
  } catch (error) {
    console.error("Error al verificar conexión Arduino:", error)
    return { conectado: false, razon: 'Error de comunicación' }
  }
}

/**
 * Función principal para cargar datos
 * Ejecuta fetchWaterLevels(), fetchPredictions() y fetchConnectionStatus() en paralelo usando Promise.all
 * Guarda las predicciones en el estado reactivo predictions
 */
const loadData = async () => {
  try {
    console.log("🚀 Iniciando carga de datos...")
    isLoading.value = true
    error.value = null
    connectionStatus.value = false

    // Cargar datos en paralelo usando Promise.all
    const [waterLevelsData, predictionsData, connectionData] = await Promise.all([
      fetchWaterLevels(),
      fetchPredictions(),
      fetchConnectionStatus()
    ])

    console.log("📊 Datos cargados:", {
      waterLevelsCount: waterLevelsData.length,
      predictionsData: predictionsData
    })

    // Verificar estado de conexión real del Arduino
    if (connectionData && connectionData.conectado) {
      connectionStatus.value = true
      console.log("✅ Arduino conectado - datos recientes")
    } else {
      connectionStatus.value = false
      console.log("❌ Arduino desconectado:", connectionData?.razon || "Sin datos de conexión")
    }

    // Guardar datos en estados reactivos
    waterLevels.value = waterLevelsData || []
    predictions.value = predictionsData.predicciones || []
    currentState.value = predictionsData.current || {}

    // Actualizar alertas visuales
    updateAlertStatus()

    console.log("💾 Estados actualizados:", {
      waterLevels: waterLevels.value.length,
      predictions: predictions.value.length,
      currentState: currentState.value
    })

    // Si el Arduino no está conectado, mostrar mensaje informativo
    if (!connectionStatus.value && !error.value) {
      error.value = 'El sensor no está enviando datos. Verifica que el Arduino esté conectado.'
    }

  } catch (err) {
    // Este catch solo se ejecutará para errores inesperados
    error.value = 'No se pueden cargar los datos del sensor. Por favor, verifica la conexión.'
    connectionStatus.value = false
    console.error('❌ Error cargando datos:', err)
    
    // Como último recurso, usar datos de fallback
    waterLevels.value = fallbackWaterLevels
    predictions.value = fallbackPredictions.predicciones
    currentState.value = fallbackPredictions.current
    
    // Actualizar alertas visuales con datos de fallback
    updateAlertStatus()
  } finally {
    isLoading.value = false
  }
}

// Computed para última actualización
const lastUpdateTime = computed(() => {
  if (waterLevels.value.length === 0) return 'Sin datos'
  const latest = waterLevels.value[waterLevels.value.length - 1]
  return latest ? formatTime(latest.timestamp) : 'Sin datos'
})

// Estado del sistema
const systemStatus = computed(() => {
  if (!connectionStatus.value) return 'Desconectado'
  if (waterLevels.value.length === 0) return 'Sin datos'
  
  const current = currentState.value.nivel_cm || parseFloat(waterLevels.value[waterLevels.value.length - 1]?.level)
  if (isNaN(current)) return 'Sin datos'
  
  if (current < 20) return 'Nivel Bajo'
  if (current > 80) return 'Nivel Alto'
  return 'Normal'
})

const systemStatusDescription = computed(() => {
  if (!connectionStatus.value) return 'Sistema fuera de línea'
  if (waterLevels.value.length === 0) return 'Esperando datos del sensor'
  
  const current = currentState.value.nivel_cm || parseFloat(waterLevels.value[waterLevels.value.length - 1]?.level)
  if (isNaN(current)) return 'Datos no válidos'
  
  if (current < 20) return 'Monitoreo de sequía activo'
  if (current > 80) return 'Alerta de inundación'
  return 'Sistema funcionando correctamente'
})

const statusColor = computed(() => {
  const status = systemStatus.value
  if (status === 'Desconectado' || status === 'Sin datos') return 'bg-gray-100'
  if (status === 'Nivel Bajo' || status === 'Nivel Alto') return 'bg-yellow-100'
  return 'bg-green-100'
})

const statusIconColor = computed(() => {
  const status = systemStatus.value
  if (status === 'Desconectado' || status === 'Sin datos') return 'text-gray-600'
  if (status === 'Nivel Bajo' || status === 'Nivel Alto') return 'text-yellow-600'
  return 'text-green-600'
})

const statusTextColor = computed(() => {
  const status = systemStatus.value
  if (status === 'Desconectado' || status === 'Sin datos') return 'text-gray-500'
  if (status === 'Nivel Bajo' || status === 'Nivel Alto') return 'text-yellow-600'
  return 'text-green-600'
})

const statusIcon = computed(() => {
  const status = systemStatus.value
  if (status === 'Desconectado') return 'M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z'
  if (status === 'Nivel Bajo' || status === 'Nivel Alto') return 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z'
  return 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
})

/**
 * Datos combinados para el gráfico principal
 * Incluye datos históricos y predicciones futuras con estilos distintos
 * Las predicciones se muestran con línea discontinua y color más claro
 */
const combinedChartData = computed(() => {
  console.log("📈 Generando datos del gráfico combinado...")
  
  // Datos históricos
  const historicalLabels = waterLevels.value.map(item => formatDate(item.timestamp))
  const historicalData = waterLevels.value.map(item => item.level)
  
  console.log("📊 Datos históricos:", {
    labels: historicalLabels.length,
    data: historicalData.length
  })
  
  // Calcular timestamps futuros para las predicciones
  const now = new Date()
  const predictionLabels = predictions.value.map(pred => {
    const futureTime = new Date(now.getTime() + pred.horizon_min * 60000)
    return formatDate(futureTime.toISOString())
  })
  const predictionData = predictions.value.map(pred => pred.nivel_cm)
  
  console.log("🔮 Predicciones para gráfico:", {
    labels: predictionLabels,
    data: predictionData,
    horizons: predictions.value.map(p => p.horizon_min)
  })
  
  // Combinar labels y datos
  const allLabels = [...historicalLabels, ...predictionLabels]
  const allHistoricalData = [...historicalData, ...new Array(predictions.value.length).fill(null)]
  const allPredictionData = [...new Array(waterLevels.value.length).fill(null), ...predictionData]
  
  const chartData = {
    labels: allLabels,
    datasets: [
      {
        label: 'Datos Históricos',
        data: allHistoricalData,
        borderColor: 'rgb(37, 99, 235)', // blue-600
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        pointBackgroundColor: 'rgb(37, 99, 235)',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Predicciones',
        data: allPredictionData,
        borderColor: 'rgb(96, 165, 250)', // blue-400 - color más claro
        backgroundColor: 'rgba(96, 165, 250, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5], // línea discontinua
        fill: false,
        tension: 0.4,
        pointBackgroundColor: 'rgb(96, 165, 250)',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }
    ]
  }
  
  console.log("📈 Datos del gráfico generados:", {
    totalLabels: chartData.labels.length,
    historicalPoints: allHistoricalData.filter(d => d !== null).length,
    predictionPoints: allPredictionData.filter(d => d !== null).length
  })
  
  return chartData
})

/**
 * Configuración del gráfico
 * Mantiene el estilo profesional con tonos de azul y gris
 */
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top',
      labels: {
        font: {
          size: 12,
          family: 'Inter, system-ui, sans-serif'
        },
        color: 'rgb(75, 85, 99)', // gray-600
        padding: 20
      }
    },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.9)', // gray-900
      titleColor: '#ffffff',
      bodyColor: '#ffffff',
      borderColor: 'rgba(75, 85, 99, 0.3)',
      borderWidth: 1,
      cornerRadius: 8,
      displayColors: true,
      titleFont: {
        size: 13,
        weight: '600'
      },
      bodyFont: {
        size: 12
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(156, 163, 175, 0.2)', // gray-400 with opacity
        borderColor: 'rgba(156, 163, 175, 0.3)'
      },
      ticks: {
        color: 'rgb(107, 114, 128)', // gray-500
        font: {
          size: 11
        },
        callback: function(value) {
          return value + ' cm'
        }
      },
      title: {
        display: true,
        text: 'Nivel (cm)',
        color: 'rgb(75, 85, 99)',
        font: {
          size: 12,
          weight: '500'
        }
      }
    },
    x: {
      grid: {
        color: 'rgba(156, 163, 175, 0.2)',
        borderColor: 'rgba(156, 163, 175, 0.3)'
      },
      ticks: {
        color: 'rgb(107, 114, 128)',
        font: {
          size: 10
        },
        maxRotation: 45
      },
      title: {
        display: true,
        text: 'Tiempo',
        color: 'rgb(75, 85, 99)',
        font: {
          size: 12,
          weight: '500'
        }
      }
    }
  },
  interaction: {
    intersect: false,
    mode: 'index'
  }
}

// Manejo de eventos de alertas
const manejarAlertaProcesada = (evento) => {
  console.log('Alerta procesada:', evento)
  
  // Mostrar notificación visual (opcional)
  if (evento.mensaje) {
    // Aquí se podría mostrar una notificación toast
    console.log('✅ ' + evento.mensaje)
  }
  
  // Opcional: Recargar datos del dashboard para reflejar cambios
  // loadData()
}

// Función para conectar WebSocket
const connectWebSocket = () => {
  const WS_URL = 'http://localhost:5000'
  
  try {
    socket = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    })
    
    socket.on('connect', () => {
      console.log('✅ WebSocket conectado')
      wsConnected.value = true
      connectionStatus.value = true
    })
    
    socket.on('disconnect', () => {
      console.log('❌ WebSocket desconectado')
      wsConnected.value = false
    })
    
    socket.on('status', (data) => {
      console.log('📡 Estado WebSocket:', data)
      if (data.connected) {
        wsConnected.value = true
      }
    })
    
    socket.on('nueva_medicion', (data) => {
      console.log('📊 Nueva medición recibida por WebSocket:', data)
      
      // Actualizar datos en tiempo real
      if (data.distancia !== undefined) {
        const nuevaMedicion = {
          level: data.distancia,
          timestamp: data.fecha || new Date().toISOString()
        }
        
        // Agregar al inicio del array
        waterLevels.value.unshift(nuevaMedicion)
        
        // Mantener solo las últimas 50 mediciones
        if (waterLevels.value.length > 50) {
          waterLevels.value = waterLevels.value.slice(0, 50)
        }
      }
      
      // Actualizar estado actual
      if (data.estado) {
        currentState.value.estado = data.estado
        currentState.value.nivel_cm = data.distancia
        updateAlertStatus()
      }
    })
    
    socket.on('cambio_estado', (data) => {
      console.log('🔄 Cambio de estado recibido por WebSocket:', data)
      
      if (data.estado) {
        currentState.value.estado = data.estado
        currentState.value.nivel_cm = data.nivel_cm
        updateAlertStatus()
      }
    })
    
    socket.on('connect_error', (error) => {
      console.error('❌ Error de conexión WebSocket:', error)
      wsConnected.value = false
    })
    
  } catch (error) {
    console.error('❌ Error inicializando WebSocket:', error)
    wsConnected.value = false
  }
}

// Lifecycle hooks
onMounted(async () => {
  await loadData()
  
  // Conectar WebSocket
  connectWebSocket()
  
  // Configurar actualización automática cada 30 segundos (fallback)
  refreshInterval = setInterval(loadData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  
  if (socket) {
    socket.disconnect()
    socket = null
  }
})
</script>

<style scoped>
/* Animaciones de alerta para inundación (rojo) */
.flood-alert {
  animation: floodBlink 1s infinite;
}

@keyframes floodBlink {
  0%, 50% {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 25%, #fca5a5 50%, #f87171 75%, #ef4444 100%);
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
  }
  25%, 75% {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 25%, #fecaca 50%, #fca5a5 75%, #f87171 100%);
    box-shadow: 0 0 30px rgba(239, 68, 68, 0.5);
  }
}

/* Animaciones de alerta para sequía (amarillo) */
.drought-alert {
  animation: droughtBlink 1.5s infinite;
}

@keyframes droughtBlink {
  0%, 50% {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 25%, #fcd34d 50%, #f59e0b 75%, #d97706 100%);
    box-shadow: 0 0 20px rgba(217, 119, 6, 0.3);
  }
  25%, 75% {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 25%, #fde68a 50%, #fcd34d 75%, #f59e0b 100%);
    box-shadow: 0 0 30px rgba(217, 119, 6, 0.5);
  }
}

/* Efecto de parpadeo más sutil para elementos internos durante alertas */
.flood-alert header,
.flood-alert main {
  animation: floodContentBlink 2s infinite;
}

.drought-alert header,
.drought-alert main {
  animation: droughtContentBlink 2.5s infinite;
}

@keyframes floodContentBlink {
  0%, 90% {
    opacity: 1;
  }
  95% {
    opacity: 0.8;
  }
  100% {
    opacity: 1;
  }
}

@keyframes droughtContentBlink {
  0%, 90% {
    opacity: 1;
  }
  95% {
    opacity: 0.85;
  }
  100% {
    opacity: 1;
  }
}

/* Indicador visual adicional en el header durante alertas */
.flood-alert .alert-indicator {
  background: linear-gradient(45deg, #ef4444, #dc2626);
  animation: alertPulse 1s infinite;
}

.drought-alert .alert-indicator {
  background: linear-gradient(45deg, #f59e0b, #d97706);
  animation: alertPulse 1.5s infinite;
}

@keyframes alertPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}
</style>