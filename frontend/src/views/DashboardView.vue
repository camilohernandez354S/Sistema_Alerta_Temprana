<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Encabezado -->
    <header class="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div class="max-w-7xl mx-auto">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold text-gray-800">
              Sistema de Alerta Temprana
            </h1>
            <p class="text-sm text-gray-600 mt-1">{{ fechaActual }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full" :class="connectionStatus ? 'bg-green-500' : 'bg-red-500'"></div>
            <span class="text-sm text-gray-600">{{ connectionStatus ? 'Conectado' : 'Desconectado' }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Contenido principal -->
    <main class="max-w-7xl mx-auto px-6 py-8">
      <!-- Estado de carga global -->
      <div v-if="isLoading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span class="ml-3 text-gray-600">Cargando datos...</span>
      </div>

      <!-- Estado de error/información global -->
      <div v-else-if="error" :class="[
        'rounded-lg p-4 mb-6',
        error.includes('demostración') ? 'bg-blue-50 border border-blue-200' : 'bg-red-50 border border-red-200'
      ]">
        <div class="flex">
          <div class="flex-shrink-0">
            <!-- Icono de información para datos de demo, error para errores reales -->
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
      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Columna izquierda: Métricas -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Tarjeta: Nivel Actual -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-sm font-medium text-gray-600">Nivel Actual</h3>
                <p class="text-2xl font-semibold text-gray-900">
                  {{ currentLevel }} <span class="text-sm text-gray-500">cm</span>
                </p>
                <p class="text-xs text-gray-500 mt-1">{{ lastUpdateTime }}</p>
              </div>
            </div>
          </div>

          <!-- Tarjeta: Tendencia -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="trendColor">
                  <svg class="w-6 h-6" :class="trendIconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="trendIcon"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-sm font-medium text-gray-600">Tendencia</h3>
                <p class="text-2xl font-semibold text-gray-900">{{ trendValue }}</p>
                <p class="text-xs mt-1" :class="trendTextColor">{{ trendDescription }}</p>
              </div>
            </div>
          </div>

          <!-- Tarjeta: Predicción -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-sm font-medium text-gray-600">Predicción Próxima</h3>
                <p class="text-2xl font-semibold text-gray-900">
                  {{ nextPrediction }} <span class="text-sm text-gray-500">cm</span>
                </p>
                <p class="text-xs text-gray-500 mt-1">{{ nextPredictionTime }}</p>
              </div>
            </div>
          </div>

          <!-- Tarjeta: Estado del Sistema -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="statusColor">
                  <svg class="w-6 h-6" :class="statusIconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="statusIcon"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-sm font-medium text-gray-600">Estado del Sistema</h3>
                <p class="text-lg font-semibold text-gray-900">{{ systemStatus }}</p>
                <p class="text-xs mt-1" :class="statusTextColor">{{ systemStatusDescription }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Columna derecha: Gráficos -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Gráfico: Niveles Históricos -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium text-gray-900">Niveles de Agua Históricos</h3>
              <div class="flex items-center space-x-2 text-sm text-gray-500">
                <div class="w-2 h-2 bg-blue-600 rounded-full"></div>
                <span>Último 24h</span>
              </div>
            </div>
            <div class="h-80">
              <Line
                v-if="waterLevelsData.labels.length > 0"
                :data="waterLevelsData"
                :options="chartOptions"
              />
              <div v-else class="flex items-center justify-center h-full text-gray-500">
                No hay datos históricos disponibles
              </div>
            </div>
          </div>

          <!-- Gráfico: Predicciones -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium text-gray-900">Predicciones de Niveles Futuros</h3>
              <div class="flex items-center space-x-2 text-sm text-gray-500">
                <div class="w-2 h-2 bg-purple-600 rounded-full"></div>
                <span>Próximas 12h</span>
              </div>
            </div>
            <div class="h-80">
              <Line
                v-if="predictionsData.labels.length > 0"
                :data="predictionsData"
                :options="chartOptions"
              />
              <div v-else class="flex flex-col items-center justify-center h-full text-gray-500">
                <svg class="w-12 h-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
                <p class="text-sm">Predicciones no disponibles</p>
                <p class="text-xs text-gray-400 mt-1">El servicio de predicción está en desarrollo</p>
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

// Intervalo para actualización automática
let refreshInterval = null

// Fecha actual
const fechaActual = computed(() => {
  return new Date().toLocaleDateString('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

// Función para formatear fecha
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Datos hardcodeados como fallback
const fallbackWaterLevels = [
  { level: 25.5, timestamp: new Date(Date.now() - 60000 * 60).toISOString() }, // hace 1 hora
  { level: 27.2, timestamp: new Date(Date.now() - 60000 * 50).toISOString() }, // hace 50 min
  { level: 28.8, timestamp: new Date(Date.now() - 60000 * 40).toISOString() }, // hace 40 min
  { level: 30.1, timestamp: new Date(Date.now() - 60000 * 30).toISOString() }, // hace 30 min
  { level: 32.4, timestamp: new Date(Date.now() - 60000 * 20).toISOString() }, // hace 20 min
  { level: 31.7, timestamp: new Date(Date.now() - 60000 * 10).toISOString() }, // hace 10 min
  { level: 33.2, timestamp: new Date().toISOString() } // ahora
]

const fallbackPredictions = [
  { predicted_level: 35.1, timestamp: new Date(Date.now() + 60000 * 30).toISOString() }, // en 30 min
  { predicted_level: 36.8, timestamp: new Date(Date.now() + 60000 * 60).toISOString() }, // en 1 hora
  { predicted_level: 38.2, timestamp: new Date(Date.now() + 60000 * 90).toISOString() }, // en 1.5 horas
  { predicted_level: 39.5, timestamp: new Date(Date.now() + 60000 * 120).toISOString() } // en 2 horas
]

// Servicio para consumir la API
const apiService = {
  async fetchWaterLevels() {
    try {
      const response = await fetch('http://localhost:5000/api/sensor/todas-lecturas')
      
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
      // El backend devuelve: { lecturas: [{ nivel_agua, estado, timestamp }] }
      // El frontend espera: { level, timestamp }
      if (Array.isArray(data)) {
        return data.map(item => ({
          level: item.nivel_agua,
          timestamp: item.timestamp
        }))
      } else if (data.lecturas && Array.isArray(data.lecturas)) {
        return data.lecturas.map(item => ({
          level: item.nivel_agua,
          timestamp: item.timestamp
        }))
      } else if (data.data && Array.isArray(data.data)) {
        return data.data.map(item => ({
          level: item.nivel_agua,
          timestamp: item.timestamp
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
  },

  async fetchPredictions() {
    try {
      const response = await fetch('http://localhost:5000/api/sensor/predicciones')
      
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
      // Asumiendo que el backend devuelve un formato similar
      if (Array.isArray(data)) {
        return data.map(item => ({
          predicted_level: item.nivel_predicho || item.predicted_level || item.nivel_agua,
          timestamp: item.timestamp
        }))
      } else if (data.data && Array.isArray(data.data)) {
        return data.data.map(item => ({
          predicted_level: item.nivel_predicho || item.predicted_level || item.nivel_agua,
          timestamp: item.timestamp
        }))
      }
      
      return []
    } catch (error) {
      console.error("Error al obtener predicciones:", error)
      
      // Si es un error de red o API no disponible, usar datos de fallback
      if (error.message.includes('fetch') || error.message.includes('HTTP') || error.message.includes('Failed to fetch')) {
        console.warn("API de predicciones no disponible, usando datos de demostración")
        return fallbackPredictions
      }
      
      throw error
    }
  }
}

// Función para insertar datos de prueba
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

// Función principal para cargar datos
const loadData = async () => {
  try {
    isLoading.value = true
    error.value = null
    connectionStatus.value = false

    // Cargar datos de niveles de agua
    let waterLevelsData = []
    let predictionsData = []
    let usingFallbackData = false

    try {
      waterLevelsData = await apiService.fetchWaterLevels()
      
      // Verificar si se están usando datos de fallback
      if (waterLevelsData === fallbackWaterLevels) {
        usingFallbackData = true
        connectionStatus.value = false
      } else {
        connectionStatus.value = true
      }
      
    } catch (waterErr) {
      console.error('Error cargando niveles de agua:', waterErr)
      
      // Mostrar error más amigable según el tipo de error
      if (waterErr.message.includes('JSON válido')) {
        error.value = 'El servidor está devolviendo datos incorrectos. Verifica que el backend esté configurado correctamente.'
      } else if (waterErr.message.includes('HTTP')) {
        error.value = `Error del servidor (${waterErr.message}). Verifica que el backend esté ejecutándose en http://localhost:5000`
      } else if (waterErr.message.includes('fetch')) {
        error.value = 'No se puede conectar con el servidor. Asegúrate de que el backend Flask esté ejecutándose.'
      } else {
        error.value = `Error inesperado: ${waterErr.message}`
      }
      
      // Usar datos de fallback en lugar de fallar completamente
      waterLevelsData = fallbackWaterLevels
      usingFallbackData = true
      connectionStatus.value = false
    }

    // Cargar predicciones (opcional - no crítico si falla)
    try {
      predictionsData = await apiService.fetchPredictions()
    } catch (predErr) {
      console.warn('Predicciones no disponibles:', predErr)
      // Si las predicciones fallan, usar datos de fallback si ya estamos en modo demo
      if (usingFallbackData) {
        predictionsData = fallbackPredictions
      } else {
        predictionsData = []
      }
    }

    waterLevels.value = waterLevelsData || []
    predictions.value = predictionsData || []

    // Si se están usando datos de demostración, mostrar mensaje informativo
    if (usingFallbackData && !error.value) {
      error.value = 'Mostrando datos de demostración. Conecta el backend para ver datos reales.'
    }

  } catch (err) {
    // Este catch solo se ejecutará para errores inesperados
    error.value = `Error crítico: ${err.message}`
    connectionStatus.value = false
    console.error('Error crítico cargando datos:', err)
    
    // Como último recurso, usar datos de fallback
    waterLevels.value = fallbackWaterLevels
    predictions.value = fallbackPredictions
  } finally {
    isLoading.value = false
  }
}

// Computed para métricas de las tarjetas
const currentLevel = computed(() => {
  if (waterLevels.value.length === 0) return 'N/A'
  const latest = waterLevels.value[waterLevels.value.length - 1]
  return latest ? latest.level.toFixed(1) : 'N/A'
})

const lastUpdateTime = computed(() => {
  if (waterLevels.value.length === 0) return 'Sin datos'
  const latest = waterLevels.value[waterLevels.value.length - 1]
  return latest ? formatTime(latest.timestamp) : 'Sin datos'
})

// Cálculo de tendencia
const trendValue = computed(() => {
  if (waterLevels.value.length < 2) return 'N/A'
  const latest = waterLevels.value[waterLevels.value.length - 1]
  const previous = waterLevels.value[waterLevels.value.length - 2]
  const diff = latest.level - previous.level
  return diff > 0 ? `+${diff.toFixed(1)} cm` : `${diff.toFixed(1)} cm`
})

const trendDescription = computed(() => {
  if (waterLevels.value.length < 2) return 'Datos insuficientes'
  const latest = waterLevels.value[waterLevels.value.length - 1]
  const previous = waterLevels.value[waterLevels.value.length - 2]
  const diff = latest.level - previous.level
  
  if (diff > 2) return 'Subida significativa'
  if (diff > 0.5) return 'Subida moderada'
  if (diff < -2) return 'Bajada significativa'
  if (diff < -0.5) return 'Bajada moderada'
  return 'Estable'
})

const trendColor = computed(() => {
  if (waterLevels.value.length < 2) return 'bg-gray-100'
  const latest = waterLevels.value[waterLevels.value.length - 1]
  const previous = waterLevels.value[waterLevels.value.length - 2]
  const diff = latest.level - previous.level
  
  if (diff > 0.5) return 'bg-green-100'
  if (diff < -0.5) return 'bg-red-100'
  return 'bg-gray-100'
})

const trendIconColor = computed(() => {
  if (waterLevels.value.length < 2) return 'text-gray-600'
  const latest = waterLevels.value[waterLevels.value.length - 1]
  const previous = waterLevels.value[waterLevels.value.length - 2]
  const diff = latest.level - previous.level
  
  if (diff > 0.5) return 'text-green-600'
  if (diff < -0.5) return 'text-red-600'
  return 'text-gray-600'
})

const trendTextColor = computed(() => {
  if (waterLevels.value.length < 2) return 'text-gray-500'
  const latest = waterLevels.value[waterLevels.value.length - 1]
  const previous = waterLevels.value[waterLevels.value.length - 2]
  const diff = latest.level - previous.level
  
  if (diff > 0.5) return 'text-green-600'
  if (diff < -0.5) return 'text-red-600'
  return 'text-gray-500'
})

const trendIcon = computed(() => {
  if (waterLevels.value.length < 2) return 'M5 12h14'
  const latest = waterLevels.value[waterLevels.value.length - 1]
  const previous = waterLevels.value[waterLevels.value.length - 2]
  const diff = latest.level - previous.level
  
  if (diff > 0.5) return 'M7 14l3-3 3 3'
  if (diff < -0.5) return 'M17 10l-3 3-3-3'
  return 'M5 12h14'
})

// Predicción próxima
const nextPrediction = computed(() => {
  if (predictions.value.length === 0) return 'N/A'
  const next = predictions.value[0]
  return next ? next.predicted_level.toFixed(1) : 'N/A'
})

const nextPredictionTime = computed(() => {
  if (predictions.value.length === 0) return 'Sin predicciones'
  const next = predictions.value[0]
  return next ? formatTime(next.timestamp) : 'Sin predicciones'
})

// Estado del sistema
const systemStatus = computed(() => {
  if (!connectionStatus.value) return 'Desconectado'
  if (waterLevels.value.length === 0) return 'Sin datos'
  
  const current = parseFloat(currentLevel.value)
  if (isNaN(current)) return 'Sin datos'
  
  if (current < 20) return 'Nivel Bajo'
  if (current > 80) return 'Nivel Alto'
  return 'Normal'
})

const systemStatusDescription = computed(() => {
  if (!connectionStatus.value) return 'Sistema fuera de línea'
  if (waterLevels.value.length === 0) return 'Esperando datos del sensor'
  
  const current = parseFloat(currentLevel.value)
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

// Datos para gráficos
const waterLevelsData = computed(() => ({
  labels: waterLevels.value.map(item => formatDate(item.timestamp)),
  datasets: [
    {
      label: 'Nivel de Agua (cm)',
      data: waterLevels.value.map(item => item.level),
      borderColor: 'rgb(37, 99, 235)', // blue-600
      backgroundColor: 'rgba(37, 99, 235, 0.1)',
      borderWidth: 2,
      fill: true,
      tension: 0.4,
      pointBackgroundColor: 'rgb(37, 99, 235)',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6
    }
  ]
}))

const predictionsData = computed(() => ({
  labels: predictions.value.map(item => formatDate(item.timestamp)),
  datasets: [
    {
      label: 'Predicción (cm)',
      data: predictions.value.map(item => item.predicted_level),
      borderColor: 'rgb(147, 51, 234)', // purple-600
      backgroundColor: 'rgba(147, 51, 234, 0.1)',
      borderWidth: 2,
      borderDash: [5, 5],
      fill: true,
      tension: 0.4,
      pointBackgroundColor: 'rgb(147, 51, 234)',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6
    }
  ]
}))

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

// Lifecycle hooks
onMounted(async () => {
  await loadData()
  
  // Configurar actualización automática cada 30 segundos
  refreshInterval = setInterval(loadData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>
