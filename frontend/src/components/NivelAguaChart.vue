<template>
  <div class="nivel-agua-chart">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-semibold text-gray-800">📊 Historial de Mediciones</h2>
      <button @click="cargarDatos" class="text-sm bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600">
        🔄 Actualizar
      </button>
    </div>
    
    <!-- Estado de carga -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span class="ml-2 text-gray-600">Cargando gráfico...</span>
    </div>
    
    <!-- Estado de error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
      <div class="text-red-600 font-medium">{{ error }}</div>
      <button @click="cargarDatos" class="mt-2 text-sm bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">
        Reintentar
      </button>
    </div>
    
    <!-- Gráfico -->
    <div v-else class="chart-container" style="height: 300px;">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart, registerables } from 'chart.js'
import { obtenerMediciones } from '../services/medicionesService'

Chart.register(...registerables)

const mediciones = ref([])
const loading = ref(true)
const error = ref(null)

const chartData = ref({
  labels: [],
  datasets: [
    {
      label: 'Nivel de agua (cm)',
      data: [],
      borderColor: '#4f8cff',
      backgroundColor: 'rgba(79,140,255,0.1)',
      tension: 0.4,
      fill: true,
      pointBackgroundColor: '#4f8cff',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2,
      pointRadius: 4
    }
  ]
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { 
      display: true,
      labels: {
        color: '#374151',
        font: { size: 12 }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0,0,0,0.8)',
      titleColor: '#ffffff',
      bodyColor: '#ffffff',
      callbacks: {
        label: function(context) {
          const value = context.parsed.y
          if (value === null || value === undefined || isNaN(value) || value < 0) {
            return 'Sin datos'
          }
          return `Nivel: ${value.toFixed(2)} cm`
        }
      }
    }
  },
  scales: {
    x: { 
      title: { 
        display: true, 
        text: 'Tiempo',
        color: '#374151'
      },
      ticks: { color: '#6B7280' }
    },
    y: { 
      title: { 
        display: true, 
        text: 'Nivel (cm)',
        color: '#374151'
      },
      ticks: { 
        color: '#6B7280',
        callback: function(value) {
          return value.toFixed(1) + ' cm'
        }
      },
      beginAtZero: true
    }
  }
}

// Función para validar mediciones
function isValidMeasurement(value) {
  return value !== null && value !== undefined && !isNaN(value) && value >= 0
}

// Función para formatear fecha para el gráfico
function formatTimeLabel(fecha) {
  try {
    const date = new Date(fecha)
    if (isNaN(date.getTime())) {
      return 'N/A'
    }
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  } catch (e) {
    return 'N/A'
  }
}

async function cargarDatos() {
  try {
    loading.value = true
    error.value = null
    
    console.log('📊 Cargando datos para el gráfico...')
    const datos = await obtenerMediciones()
    
    if (!datos || datos.length === 0) {
      console.warn('⚠️ No hay mediciones disponibles')
      chartData.value.labels = ['Sin datos']
      chartData.value.datasets[0].data = [0]
      return
    }
    
    // Filtrar solo mediciones válidas y tomar las últimas 20
    const medicionesValidas = datos
      .filter(m => isValidMeasurement(m.distancia))
      .slice(0, 20)
      .reverse() // Mostrar cronológicamente
    
    if (medicionesValidas.length === 0) {
      console.warn('⚠️ No hay mediciones válidas')
      chartData.value.labels = ['Sin datos válidos']
      chartData.value.datasets[0].data = [0]
      return
    }
    
    // Preparar datos para el gráfico
    const labels = medicionesValidas.map(m => formatTimeLabel(m.fecha))
    const datos_grafico = medicionesValidas.map(m => parseFloat(m.distancia.toFixed(2)))
    
    chartData.value.labels = labels
    chartData.value.datasets[0].data = datos_grafico
    
    console.log(`✅ Gráfico actualizado con ${medicionesValidas.length} mediciones válidas`)
    
  } catch (e) {
    console.error('❌ Error cargando datos del gráfico:', e)
    error.value = 'Error cargando datos del gráfico'
    chartData.value.labels = ['Error']
    chartData.value.datasets[0].data = [0]
  } finally {
    loading.value = false
  }
}

onMounted(cargarDatos)
</script>

<style scoped>
.nivel-agua-chart {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.chart-container {
  position: relative;
  width: 100%;
}

/* Asegurar que el gráfico sea responsive */
.chart-container canvas {
  max-width: 100% !important;
  height: auto !important;
}
</style>
