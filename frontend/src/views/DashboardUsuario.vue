<template>
  <DashboardLayout>
    <div class="max-w-3xl mx-auto mt-8 space-y-6">
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatsCard title="Última medición" :value="ultimaMedicion" accent="blue" />
        <StatsCard title="Estado actual" :value="estadoActual" accent="green" />
        <StatsCard title="Fecha/Hora" :value="fechaActual" accent="gray" />
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white rounded-xl shadow p-3 flex items-center justify-center min-h-[160px]">
          <NivelAguaChart />
        </div>
        <div class="bg-white rounded-xl shadow p-3 flex items-center justify-center min-h-[160px]">
          <!-- Aquí puedes poner un gráfico secundario o información relevante -->
          <span class="text-gray-400 text-sm">Gráfico secundario</span>
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
const estadoActual = ref('--')
const fechaActual = ref('--')

onMounted(async () => {
  // Aquí puedes cargar datos reales si lo deseas
  ultimaMedicion.value = '44 cm'
  estadoActual.value = 'Normal'
  fechaActual.value = '2025-09-21 23:00'
})
</script>

<style scoped>
.dashboard-usuario {
  padding: 2rem;
}
.cards {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}
</style>
