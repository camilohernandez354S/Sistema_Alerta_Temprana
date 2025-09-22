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
      <!-- Resumen de Mediciones -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <div class="text-3xl font-bold text-blue-600 mb-2">{{ ultimaMedicion }}</div>
          <div class="text-gray-500 text-sm">Última medición</div>
        </div>
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <div class="text-2xl font-bold text-green-600 mb-2">{{ promedio }}</div>
          <div class="text-gray-500 text-sm">Promedio</div>
        </div>
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <div class="text-2xl font-bold text-red-600 mb-2">{{ maximo }}</div>
          <div class="text-gray-500 text-sm">Máximo</div>
        </div>
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <div class="text-2xl font-bold text-yellow-600 mb-2">{{ minimo }}</div>
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
          <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">📊 Historial de Mediciones</h2>
            <NivelAguaChart />
          </div>
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

function handleLogout() {
  logout()
  router.push('/login')
}

onMounted(async () => {
  // Saludo personalizado
  try {
    const resp = await fetch('http://localhost:5000/api/saludo-admin', {
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
