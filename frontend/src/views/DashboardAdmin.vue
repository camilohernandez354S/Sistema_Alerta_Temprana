<template>
  <DashboardLayout>
    <div class="max-w-4xl mx-auto mt-8 space-y-6">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatsCard title="Última medición" :value="ultimaMedicion" accent="blue" />
        <StatsCard title="Promedio" :value="promedio" accent="green" />
        <StatsCard title="Máximo" :value="maximo" accent="red" />
        <StatsCard title="Mínimo" :value="minimo" accent="yellow" />
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white rounded-xl shadow p-3 flex items-center justify-center min-h-[160px]">
          <NivelAguaChart />
        </div>
        <div class="flex flex-col gap-4">
          <div class="bg-white rounded-xl shadow p-3 flex-1 flex items-center justify-center min-h-[70px]">
            <span class="text-gray-400 text-sm">Gráfico secundario</span>
          </div>
          <div class="bg-white rounded-xl shadow p-3 flex-1 flex items-center justify-center min-h-[70px]">
            <span class="text-gray-400 text-sm">Panel de control</span>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import DashboardLayout from '../layouts/DashboardLayout.vue'
import StatsCard from '../components/StatsCard.vue'
import NivelAguaChart from '../components/NivelAguaChart.vue'
import { ref, onMounted } from 'vue'
import { obtenerMediciones } from '../services/medicionesService'

const ultimaMedicion = ref('--')
const promedio = ref('--')
const maximo = ref('--')
const minimo = ref('--')

onMounted(async () => {
  // Aquí puedes cargar datos reales si lo deseas
  ultimaMedicion.value = '44 cm'
  promedio.value = '43.2 cm'
  maximo.value = '46 cm'
  minimo.value = '41 cm'
})
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
