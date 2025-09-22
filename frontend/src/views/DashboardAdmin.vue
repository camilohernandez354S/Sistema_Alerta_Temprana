<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <!-- Header -->
    <div class="w-full flex justify-between items-center px-8 mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-800">Sistema de Alerta Temprana</h1>
        <p class="text-lg text-gray-600">Panel de Administrador</p>
        <div v-if="saludo" class="mt-2 text-green-700 font-semibold">{{ saludo }}</div>
      </div>
      <button @click="handleLogout" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
        Cerrar sesión
      </button>
    </div>

    <div class="px-8">
      <!-- Mensaje de error de conexión -->
      <div v-if="connectionError" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error de conexión</h3>
            <p class="mt-1 text-sm text-red-700">
              No se pueden obtener datos del sensor. Verifica que el sistema esté funcionando correctamente.
            </p>
          </div>
        </div>
      </div>
      
      <!-- Resumen de Mediciones -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <div class="text-3xl font-bold mb-2" :class="ultimaMedicionColor">{{ ultimaMedicion }}</div>
          <div class="text-gray-500 text-sm">Última medición</div>
        </div>
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <div class="text-2xl font-bold mb-2" :class="promedioColor">{{ promedio }}</div>
          <div class="text-gray-500 text-sm">Promedio</div>
        </div>
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <div class="text-2xl font-bold mb-2" :class="maximoColor">{{ maximo }}</div>
          <div class="text-gray-500 text-sm">Máximo</div>
        </div>
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <div class="text-2xl font-bold mb-2" :class="minimoColor">{{ minimo }}</div>
          <div class="text-gray-500 text-sm">Mínimo</div>
        </div>
      </div>

      <!-- Layout de dos columnas -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Panel de Alertas -->
        <div class="lg:col-span-1">
          <AlertsPanel />
        </div>

        <!-- Gráfico de Nivel de Agua -->
        <div class="lg:col-span-1">
          <NivelAguaChart />
        </div>
      </div>
    </div>
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
