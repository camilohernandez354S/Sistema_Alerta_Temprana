<template>
  <div class="nivel-agua-chart">
    <h2>Nivel de Agua (Gráfico)</h2>
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart, registerables } from 'chart.js'
import { obtenerMediciones } from '../services/medicionesService'

Chart.register(...registerables)

const mediciones = ref([])
const chartData = ref({
  labels: [],
  datasets: [
    {
      label: 'Nivel de agua (cm)',
      data: [],
      borderColor: '#4f8cff',
      backgroundColor: 'rgba(79,140,255,0.2)',
      tension: 0.3,
      fill: true
    }
  ]
})

const chartOptions = {
  responsive: true,
  plugins: {
    legend: { display: true }
  },
  scales: {
    x: { title: { display: true, text: 'Hora' } },
    y: { title: { display: true, text: 'cm' } }
  }
}

async function cargarDatos() {
  mediciones.value = await obtenerMediciones()
  chartData.value.labels = mediciones.value.map(m => m.fecha.split('T')[1].split('Z')[0])
  chartData.value.datasets[0].data = mediciones.value.map(m => m.distancia)
}

onMounted(cargarDatos)
</script>

<style scoped>
.nivel-agua-chart {
  margin-bottom: 2rem;
  color: #fff;
  background: #222;
  border-radius: 8px;
  padding: 1rem;
}
</style>
