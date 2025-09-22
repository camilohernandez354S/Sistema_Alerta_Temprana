<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
    <!-- Header mejorado -->
    <header class="bg-white/80 backdrop-blur-sm shadow-lg border-b border-blue-200/50 px-6 py-6">
      <div class="max-w-7xl mx-auto">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                </svg>
              </div>
              <div>
                <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Panel de Administrador
                </h1>
                <p class="text-sm text-gray-600 mt-1 flex items-center space-x-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                  <span>Sistema de Alerta Temprana</span>
                </p>
                <div v-if="saludo" class="mt-2 text-sm text-emerald-700 font-medium bg-emerald-50 rounded-full px-3 py-1 inline-block">
                  {{ saludo }}
                </div>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-3 bg-white/60 backdrop-blur-sm rounded-full px-4 py-2 shadow-sm border border-gray-200/50">
              <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <span class="text-sm font-medium text-emerald-700">Administrador</span>
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
      <!-- Mensaje de error de conexión mejorado -->
      <div v-if="connectionError" class="bg-red-50/80 backdrop-blur-sm border border-red-200/50 rounded-2xl p-6 mb-8 shadow-lg">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <div class="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center">
              <svg class="h-6 w-6 text-red-600" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-red-800 mb-2">Error de Conexión</h3>
            <p class="text-sm text-red-700 mb-3">
              No se pueden obtener datos del sensor. Verifica que el sistema esté funcionando correctamente.
            </p>
            <button @click="refreshData" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors duration-200 text-sm font-medium">
              Reintentar Conexión
            </button>
          </div>
        </div>
      </div>
      
      <!-- Resumen de Mediciones mejorado -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Resumen de Mediciones</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <!-- Última medición -->
          <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 hover:shadow-2xl transition-all duration-300 group">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-200">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <div class="text-right">
                <div class="text-3xl font-bold" :class="ultimaMedicionColor">{{ ultimaMedicion }}</div>
                <div class="text-sm text-gray-500 font-medium">Última medición</div>
              </div>
            </div>
            <div class="text-xs text-gray-600">Datos en tiempo real</div>
          </div>

          <!-- Promedio -->
          <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 hover:shadow-2xl transition-all duration-300 group">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-200">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <div class="text-right">
                <div class="text-3xl font-bold" :class="promedioColor">{{ promedio }}</div>
                <div class="text-sm text-gray-500 font-medium">Promedio</div>
              </div>
            </div>
            <div class="text-xs text-gray-600">Valor promedio histórico</div>
          </div>

          <!-- Máximo -->
          <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 hover:shadow-2xl transition-all duration-300 group">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-200">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"></path>
                </svg>
              </div>
              <div class="text-right">
                <div class="text-3xl font-bold" :class="maximoColor">{{ maximo }}</div>
                <div class="text-sm text-gray-500 font-medium">Máximo</div>
              </div>
            </div>
            <div class="text-xs text-gray-600">Valor más alto registrado</div>
          </div>

          <!-- Mínimo -->
          <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 hover:shadow-2xl transition-all duration-300 group">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-200">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 13l-5 5m0 0l-5-5m5 5V6"></path>
                </svg>
              </div>
              <div class="text-right">
                <div class="text-3xl font-bold" :class="minimoColor">{{ minimo }}</div>
                <div class="text-sm text-gray-500 font-medium">Mínimo</div>
              </div>
            </div>
            <div class="text-xs text-gray-600">Valor más bajo registrado</div>
          </div>
        </div>
      </div>

      <!-- Layout de dos columnas mejorado -->
      <div class="space-y-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Análisis y Monitoreo</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Panel de Alertas -->
          <div class="lg:col-span-1">
            <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 hover:shadow-2xl transition-all duration-300">
              <div class="flex items-center mb-4">
                <div class="w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center shadow-lg mr-3">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-bold text-gray-800">Panel de Alertas</h3>
              </div>
              <AlertsPanel />
            </div>
          </div>

          <!-- Gráfico de Nivel de Agua -->
          <div class="lg:col-span-1">
            <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 hover:shadow-2xl transition-all duration-300">
              <div class="flex items-center mb-4">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg mr-3">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-bold text-gray-800">Gráfico de Nivel de Agua</h3>
              </div>
              <NivelAguaChart />
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import NivelAguaChart from '../components/NivelAguaChart.vue'
import AlertsPanel from '../components/AlertsPanel.vue'
import { ref, onMounted } from 'vue'
import { obtenerMediciones } from '../services/medicionesService'
import { getToken, logout } from '../services/authService'
import { useRouter } from 'vue-router'

const ultimaMedicion = ref('--')
const promedio = ref('--')
const maximo = ref('--')
const minimo = ref('--')
const saludo = ref('')
const router = useRouter()
const connectionError = ref(false)

// Función para validar si una medición es válida
function isValidMeasurement(value) {
  return value !== null && value !== undefined && !isNaN(value) && value >= 0
}

// Función para formatear mediciones con 2 decimales consistentes
function formatMeasurement(value) {
  if (!isValidMeasurement(value)) {
    return 'Sin datos'
  }
  return value.toFixed(2) + ' cm'
}

// Función para obtener color según el rango de medición
function getMeasurementColor(value) {
  if (!isValidMeasurement(value)) {
    return 'text-gray-400'
  }
  
  if (value <= 200) {
    return 'text-green-600'  // Verde - Normal
  } else if (value <= 400) {
    return 'text-orange-500' // Naranja - Alerta
  } else {
    return 'text-red-600'    // Rojo - Crítico
  }
}

function handleLogout() {
  logout()
  router.push('/login')
}

// Función para refrescar datos
async function refreshData() {
  try {
    connectionError.value = false
    const mediciones = await obtenerMediciones()
    
    if (mediciones.length > 0) {
      const medicionesValidas = mediciones.filter(m => isValidMeasurement(m.distancia))
      
      if (medicionesValidas.length > 0) {
        const ultimaDistancia = medicionesValidas[0].distancia
        ultimaMedicion.value = formatMeasurement(ultimaDistancia)
        ultimaMedicionColor.value = getMeasurementColor(ultimaDistancia)
        
        const distanciasValidas = medicionesValidas.map(m => m.distancia)
        const promedioValue = distanciasValidas.reduce((a, b) => a + b, 0) / distanciasValidas.length
        promedio.value = formatMeasurement(promedioValue)
        promedioColor.value = getMeasurementColor(promedioValue)
        
        const maximoValue = Math.max(...distanciasValidas)
        maximo.value = formatMeasurement(maximoValue)
        maximoColor.value = getMeasurementColor(maximoValue)
        
        const minimoValue = Math.min(...distanciasValidas)
        minimo.value = formatMeasurement(minimoValue)
        minimoColor.value = getMeasurementColor(minimoValue)
      } else {
        setNoDataState()
      }
    } else {
      setNoDataState()
    }
  } catch (e) {
    console.error('Error refrescando datos:', e)
    setConnectionErrorState()
  }
}

// Variables reactivas para colores
const ultimaMedicionColor = ref('text-gray-400')
const promedioColor = ref('text-gray-400')
const maximoColor = ref('text-gray-400')
const minimoColor = ref('text-gray-400')

onMounted(async () => {
  // Saludo personalizado
  try {
    const resp = await fetch('http://localhost:5000/api/saludo-usuario', {
      headers: { 'Authorization': 'Bearer ' + getToken() }
    })
    const data = await resp.json()
    if (resp.ok) {
      saludo.value = data.mensaje
    } else {
      saludo.value = data.error || 'Error de autenticación'
    }
  } catch (e) {
    saludo.value = 'Error de conexión'
  }

  // Mediciones con validación y formato mejorado
  try {
    const mediciones = await obtenerMediciones()
    
    if (mediciones.length > 0) {
      // Filtrar solo mediciones válidas
      const medicionesValidas = mediciones.filter(m => isValidMeasurement(m.distancia))
      
      if (medicionesValidas.length > 0) {
        // Última medición
        const ultimaDistancia = medicionesValidas[0].distancia
        ultimaMedicion.value = formatMeasurement(ultimaDistancia)
        ultimaMedicionColor.value = getMeasurementColor(ultimaDistancia)
        
        // Calcular estadísticas solo con datos válidos
        const distanciasValidas = medicionesValidas.map(m => m.distancia)
        
        // Promedio con precisión optimizada
        const promedioValue = distanciasValidas.reduce((a, b) => a + b, 0) / distanciasValidas.length
        promedio.value = formatMeasurement(promedioValue)
        promedioColor.value = getMeasurementColor(promedioValue)
        
        // Máximo
        const maximoValue = Math.max(...distanciasValidas)
        maximo.value = formatMeasurement(maximoValue)
        maximoColor.value = getMeasurementColor(maximoValue)
        
        // Mínimo
        const minimoValue = Math.min(...distanciasValidas)
        minimo.value = formatMeasurement(minimoValue)
        minimoColor.value = getMeasurementColor(minimoValue)
        
        connectionError.value = false
      } else {
        // No hay mediciones válidas
        setNoDataState()
      }
    } else {
      // No hay mediciones
      setNoDataState()
    }
  } catch (e) {
    console.error('Error obteniendo mediciones:', e)
    setConnectionErrorState()
  }
})

// Función para establecer estado sin datos
function setNoDataState() {
  ultimaMedicion.value = 'Sin datos'
  promedio.value = 'Sin datos'
  maximo.value = 'Sin datos'
  minimo.value = 'Sin datos'
  
  ultimaMedicionColor.value = 'text-gray-400'
  promedioColor.value = 'text-gray-400'
  maximoColor.value = 'text-gray-400'
  minimoColor.value = 'text-gray-400'
  
  connectionError.value = false
}

// Función para establecer estado de error de conexión
function setConnectionErrorState() {
  ultimaMedicion.value = ''
  promedio.value = ''
  maximo.value = ''
  minimo.value = ''
  
  ultimaMedicionColor.value = 'text-gray-400'
  promedioColor.value = 'text-gray-400'
  maximoColor.value = 'text-gray-400'
  minimoColor.value = 'text-gray-400'
  
  connectionError.value = true
  saludo.value = 'Error de conexión con el servidor'
}
</script>

<style scoped>
.dashboard-admin {
  padding: 2rem;
}
.cards {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}
.panel-control {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
}
</style>
