<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-8">
    <div class="w-full flex justify-end px-8 mb-2">
      <button @click="handleLogout" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">Cerrar sesión</button>
    </div>
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Sistema de Alerta Temprana</h1>
    <div v-if="saludo" class="mb-4 text-green-700 font-semibold">{{ saludo }}</div>
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
import { getToken, logout } from '../services/authService'
import { useRouter } from 'vue-router'

const ultimaMedicion = ref('--')
const promedio = ref('--')
const maximo = ref('--')
const minimo = ref('--')
const saludo = ref('')
const router = useRouter()

function handleLogout() {
  logout()
  router.push('/login')
}

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

  // Mediciones
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
.dashboard-usuario {
  padding: 2rem;
}
.cards {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}
</style>

