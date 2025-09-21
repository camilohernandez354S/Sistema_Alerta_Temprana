<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Sidebar -->
    <div class="w-64 bg-slate-800 text-white flex-shrink-0 hidden lg:block">
      <div class="p-6">
        <div class="flex items-center space-x-2 mb-8">
          <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-sm">SA</span>
          </div>
          <span class="font-semibold text-lg">Sistema Alerta</span>
        </div>
        
        <nav class="space-y-2">
          <a href="#" class="flex items-center space-x-3 px-4 py-3 rounded-lg bg-slate-700 text-white">
            <span class="text-lg">🏠</span>
            <span class="font-medium">Inicio</span>
          </a>
          <a href="#" class="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-slate-700 text-slate-300 hover:text-white transition-colors">
            <span class="text-lg">📊</span>
            <span class="font-medium">Dashboard</span>
          </a>
          <a href="#" class="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-slate-700 text-slate-300 hover:text-white transition-colors">
            <span class="text-lg">📋</span>
            <span class="font-medium">Reportes</span>
          </a>
          <a href="#" class="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-slate-700 text-slate-300 hover:text-white transition-colors">
            <span class="text-lg">⚙️</span>
            <span class="font-medium">Configuración</span>
          </a>
        </nav>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="flex-1 flex flex-col min-h-screen">
      <!-- Encabezado superior -->
      <header class="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold text-gray-800">
              Sistema de Alerta Temprana – Niveles de Agua
            </h1>
            <p class="text-sm text-gray-600 mt-1">{{ fechaActual }}</p>
          </div>
          <button class="bg-slate-700 hover:bg-slate-800 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2">
            <span>📤</span>
            <span>Exportar datos</span>
          </button>
        </div>
      </header>

      <!-- Área principal -->
      <main class="flex-1 p-6 space-y-6">
        <!-- Sección de métricas rápidas -->
        <section>
          <h2 class="text-lg font-semibold text-gray-800 mb-4">Métricas Actuales</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div
              v-for="lectura in lecturas"
              :key="lectura.id"
              class="bg-white rounded-xl shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow"
            >
              <div class="flex items-center justify-between mb-4">
                <div class="text-2xl text-gray-400">{{ getIcon(lectura.estado) }}</div>
                <span class="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                  {{ lectura.fecha }}
                </span>
              </div>
              <h3 class="text-sm font-medium text-gray-600 mb-1">{{ lectura.estado }}</h3>
              <p class="text-2xl font-semibold text-gray-800">{{ lectura.nivel }} <span class="text-sm text-gray-500">cm</span></p>
            </div>
          </div>
        </section>

        <!-- Sección de gráficos -->
        <section>
          <h2 class="text-lg font-semibold text-gray-800 mb-4">Análisis de Datos</h2>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Gráfico de líneas -->
            <div class="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <h3 class="text-base font-medium text-gray-800 mb-4">
                Evolución del Nivel de Agua
              </h3>
              <div class="h-80">
                <Line
                  :data="lineChartData"
                  :options="lineChartOptions"
                />
              </div>
            </div>

            <!-- Gráfico de barras -->
            <div class="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <h3 class="text-base font-medium text-gray-800 mb-4">
                Comparación de Niveles
              </h3>
              <div class="h-80">
                <Bar
                  :data="barChartData"
                  :options="barChartOptions"
                />
              </div>
            </div>

            <!-- Gráfico circular -->
            <div class="bg-white rounded-xl shadow-md p-6 border border-gray-200 lg:col-span-2">
              <h3 class="text-base font-medium text-gray-800 mb-4 text-center">
                Distribución de Estados
              </h3>
              <div class="flex justify-center">
                <div class="w-80 h-80">
                  <Doughnut
                    :data="doughnutChartData"
                    :options="doughnutChartOptions"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { Line, Bar, Doughnut } from 'vue-chartjs'

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

// Datos hardcodeados
const lecturas = ref([
  { id: 1, nivel: 30, estado: "Normal", fecha: "2025-09-18" },
  { id: 2, nivel: 10, estado: "Sequía", fecha: "2025-09-19" },
  { id: 3, nivel: 85, estado: "Inundación", fecha: "2025-09-20" },
  { id: 4, nivel: 45, estado: "Normal", fecha: "2025-09-21" }
])

// Fecha actual
const fechaActual = computed(() => {
  return new Date().toLocaleDateString('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

// Funciones para tarjetas
const getIcon = (estado) => {
  switch (estado) {
    case 'Normal': return '💧'
    case 'Sequía': return '☀️'
    case 'Inundación': return '🌊'
    default: return '💧'
  }
}

// Configuración del gráfico de líneas
const lineChartData = computed(() => ({
  labels: lecturas.value.map(l => l.fecha),
  datasets: [
    {
      label: 'Nivel de Agua (cm)',
      data: lecturas.value.map(l => l.nivel),
      borderColor: 'rgb(71, 85, 105)', // slate-600
      backgroundColor: 'rgba(71, 85, 105, 0.1)',
      borderWidth: 2,
      fill: true,
      tension: 0.3,
      pointBackgroundColor: 'rgb(71, 85, 105)',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6
    }
  ]
}))

const lineChartOptions = {
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
        color: 'rgb(75, 85, 99)' // gray-600
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(156, 163, 175, 0.3)', // gray-400 with opacity
        borderColor: 'rgba(156, 163, 175, 0.5)'
      },
      ticks: {
        color: 'rgb(107, 114, 128)', // gray-500
        font: {
          size: 11
        }
      }
    },
    x: {
      grid: {
        color: 'rgba(156, 163, 175, 0.3)',
        borderColor: 'rgba(156, 163, 175, 0.5)'
      },
      ticks: {
        color: 'rgb(107, 114, 128)',
        font: {
          size: 11
        }
      }
    }
  }
}

// Configuración del gráfico de barras
const barChartData = computed(() => ({
  labels: lecturas.value.map(l => l.fecha),
  datasets: [
    {
      label: 'Nivel de Agua (cm)',
      data: lecturas.value.map(l => l.nivel),
      backgroundColor: lecturas.value.map(l => {
        switch (l.estado) {
          case 'Normal': return 'rgba(71, 85, 105, 0.7)' // slate-600
          case 'Sequía': return 'rgba(156, 163, 175, 0.7)' // gray-400
          case 'Inundación': return 'rgba(55, 65, 81, 0.7)' // gray-700
          default: return 'rgba(71, 85, 105, 0.7)'
        }
      }),
      borderColor: lecturas.value.map(l => {
        switch (l.estado) {
          case 'Normal': return 'rgb(71, 85, 105)'
          case 'Sequía': return 'rgb(156, 163, 175)'
          case 'Inundación': return 'rgb(55, 65, 81)'
          default: return 'rgb(71, 85, 105)'
        }
      }),
      borderWidth: 1,
      borderRadius: 4,
      borderSkipped: false
    }
  ]
}))

const barChartOptions = {
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
        color: 'rgb(75, 85, 99)' // gray-600
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(156, 163, 175, 0.3)',
        borderColor: 'rgba(156, 163, 175, 0.5)'
      },
      ticks: {
        color: 'rgb(107, 114, 128)',
        font: {
          size: 11
        }
      }
    },
    x: {
      grid: {
        display: false
      },
      ticks: {
        color: 'rgb(107, 114, 128)',
        font: {
          size: 11
        }
      }
    }
  }
}

// Configuración del gráfico circular
const doughnutChartData = computed(() => {
  const estados = {}
  lecturas.value.forEach(l => {
    estados[l.estado] = (estados[l.estado] || 0) + 1
  })

  return {
    labels: Object.keys(estados),
    datasets: [
      {
        data: Object.values(estados),
        backgroundColor: [
          'rgba(71, 85, 105, 0.8)',   // Normal - slate-600
          'rgba(156, 163, 175, 0.8)', // Sequía - gray-400
          'rgba(55, 65, 81, 0.8)'     // Inundación - gray-700
        ],
        borderColor: [
          'rgb(71, 85, 105)',
          'rgb(156, 163, 175)',
          'rgb(55, 65, 81)'
        ],
        borderWidth: 2,
        hoverOffset: 8,
        hoverBorderWidth: 3
      }
    ]
  }
})

const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        padding: 16,
        font: {
          size: 12,
          family: 'Inter, system-ui, sans-serif'
        },
        color: 'rgb(75, 85, 99)', // gray-600
        usePointStyle: true,
        pointStyle: 'circle'
      }
    }
  },
  cutout: '65%',
  elements: {
    arc: {
      borderJoinStyle: 'round'
    }
  }
}
</script>
