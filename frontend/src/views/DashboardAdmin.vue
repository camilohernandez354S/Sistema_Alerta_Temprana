<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-8">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Sistema de Alerta Temprana (Admin)</h1>
    <div class="bg-white rounded-xl shadow p-6 w-full max-w-md mb-6 flex flex-col items-center">
      <div class="text-4xl font-bold text-blue-600 mb-2">{{ ultimaMedicion }}</div>
      <div class="text-gray-500 text-sm mb-4">Última distancia medida</div>
      <div class="flex justify-between w-full text-center text-sm text-gray-600">
        <div>
          <div class="font-semibold">Promedio</div>
          <div>{{ promedio }}</div>
        </div>
        <div>
          <div class="font-semibold">Máximo</div>
          <div>{{ maximo }}</div>
        </div>
        <div>
          <div class="font-semibold">Mínimo</div>
          <div>{{ minimo }}</div>
        </div>
      </div>
    </div>
    <div class="bg-white rounded-xl shadow p-4 w-full max-w-2xl">
      <NivelAguaChart />
    </div>
  </div>
</template>

<script setup>
import NivelAguaChart from '../components/NivelAguaChart.vue'
import { ref, onMounted } from 'vue'
import { obtenerMediciones } from '../services/medicionesService'

const ultimaMedicion = ref('--')
const promedio = ref('--')
const maximo = ref('--')
const minimo = ref('--')

onMounted(async () => {
  const mediciones = await obtenerMediciones()
  if (mediciones.length > 0) {
    ultimaMedicion.value = mediciones[0].distancia + ' cm'
    const distancias = mediciones.map(m => m.distancia)
    promedio.value = (distancias.reduce((a, b) => a + b, 0) / distancias.length).toFixed(1) + ' cm'
    maximo.value = Math.max(...distancias) + ' cm'
    minimo.value = Math.min(...distancias) + ' cm'
  }
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
