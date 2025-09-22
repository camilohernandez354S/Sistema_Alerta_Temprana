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
            <button @click="handleLogout" class="bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600 ml-6">Cerrar sesión</button>
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
          <!-- Estado actual - Card grande -->
          <div class="lg:col-span-1">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div class="text-center">
                <h3 class="text-sm font-medium text-gray-600 mb-4">Estado Actual</h3>
                
                <!-- Nivel actual en texto grande -->
                <div class="mb-4">
                  <div class="text-4xl font-bold text-gray-900">
                    {{ currentState.nivel_cm || 'N/A' }}
                  </div>
                  <div class="text-sm text-gray-500">cm</div>
                </div>
                
                <!-- Estado textual -->
                <div class="mb-3">
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium" 
                        :class="getStateColorClass(currentState.estado)">
                    {{ currentState.estado || 'Sin datos' }}
                  </span>
                </div>
                
                <!-- Tendencia -->
                <div class="flex items-center justify-center space-x-2">
                  <svg class="w-4 h-4" :class="getTrendIconColor(currentState.tendencia)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getTrendIcon(currentState.tendencia)"></path>
                  </svg>
                  <span class="text-sm text-gray-600">{{ getTrendText(currentState.tendencia) }}</span>
                </div>
                
                <!-- Pendiente si está disponible -->
                <div v-if="currentState.pendiente_cm_por_h !== undefined" class="mt-2 text-xs text-gray-500">
                  {{ currentState.pendiente_cm_por_h > 0 ? '+' : '' }}{{ currentState.pendiente_cm_por_h?.toFixed(1) }} cm/h
                </div>
              </div>
            </div>
          </div>
          
          <!-- Predicciones futuras - Tarjetas pequeñas -->
          <div class="lg:col-span-3">
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              <div v-for="prediction in predictions" :key="prediction.horizon_min" 
                   class="bg-gray-50 rounded-xl shadow-sm border border-gray-200 p-4">
                <div class="text-center">
                  <!-- Horizonte temporal -->
                  <div class="text-sm font-medium text-gray-600 mb-2">
                    {{ formatHorizon(prediction.horizon_min) }}
                  </div>
                  
                  <!-- Nivel predicho -->
                  <div class="text-2xl font-semibold text-gray-800 mb-2">
                    {{ prediction.nivel_cm?.toFixed(1) || 'N/A' }} cm
                  </div>
                  
                  <!-- Estado y confianza -->
                  <div class="space-y-1">
                    <div>
                      <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium" 
                            :class="getStateColorClass(prediction.estado)">
                        {{ prediction.estado || 'Sin datos' }}
                      </span>
                    </div>
                    <div class="text-xs text-gray-500">
                      Confianza: {{ Math.round((prediction.confianza || 0) * 100) }}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Gráfico principal con datos históricos y predicciones -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Niveles de Agua - Histórico y Predicciones</h3>
            <div class="flex items-center space-x-4 text-sm text-gray-500">
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-blue-600 rounded-full"></div>
                <span>Histórico</span>
              </div>
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span>Predicciones</span>
              </div>
            </div>
          </div>
          <div class="h-96">
            <Line
              v-if="combinedChartData.labels.length > 0"
              :data="combinedChartData"
              :options="chartOptions"
            />
            <div v-else class="flex items-center justify-center h-full text-gray-500">
              No hay datos disponibles
            </div>
          </div>
        </div>

        <!-- Métricas adicionales -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Última actualización -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-sm font-medium text-gray-600">Última Actualización</h3>
                <p class="text-lg font-semibold text-gray-900">{{ lastUpdateTime }}</p>
                <p class="text-xs text-gray-500 mt-1">Datos del sensor</p>
              </div>
            </div>
          </div>

          <!-- Estado del sistema -->
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

          <!-- Datos de predicción -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <h3 class="text-sm font-medium text-gray-600">Predicciones</h3>
                <p class="text-lg font-semibold text-gray-900">{{ predictions.length }}</p>
                <p class="text-xs text-gray-500 mt-1">Horizontes disponibles</p>
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