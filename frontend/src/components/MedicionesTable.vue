<template>
  <div class="mediciones-table bg-[#fcffff] border border-[#c4dafa] rounded-lg p-4 sm:p-5 md:p-6">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 sm:mb-5 md:mb-6 gap-3 sm:gap-4">
      <div class="flex items-center space-x-2 sm:space-x-3">
        <div class="w-9 h-9 sm:w-10 sm:h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center flex-shrink-0">
          <svg class="w-4 h-4 sm:w-5 sm:h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
          </svg>
        </div>
        <h2 class="text-lg sm:text-xl font-semibold text-[#005187]">Historial de Mediciones</h2>
      </div>
      <button 
        @click="cargarMediciones" 
        :disabled="loading"
        class="w-full sm:w-auto px-4 py-2 bg-[#005187] text-white rounded-lg hover:bg-[#4d82bc] transition-colors duration-150 disabled:opacity-50 flex items-center justify-center space-x-2 font-medium text-sm sm:text-base"
      >
        <svg v-if="loading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>{{ loading ? 'Cargando...' : 'Actualizar' }}</span>
      </button>
    </div>

    <!-- Tabla de mediciones -->
    <div class="overflow-x-auto bg-[#c4dafa] rounded-lg p-2 sm:p-3 md:p-4">
      <table class="w-full min-w-[640px]">
        <thead>
          <tr class="border-b border-[#84b6f4] bg-[#fcffff]">
            <th class="text-left py-2 sm:py-3 px-2 sm:px-3 md:px-4 text-xs sm:text-sm font-semibold text-[#005187]">Fecha y Hora</th>
            <th class="text-left py-2 sm:py-3 px-2 sm:px-3 md:px-4 text-xs sm:text-sm font-semibold text-[#005187]">Nivel (cm)</th>
            <th class="text-left py-2 sm:py-3 px-2 sm:px-3 md:px-4 text-xs sm:text-sm font-semibold text-[#005187] hidden sm:table-cell">Estado</th>
            <th class="text-left py-2 sm:py-3 px-2 sm:px-3 md:px-4 text-xs sm:text-sm font-semibold text-[#005187] hidden md:table-cell">Sensor ID</th>
            <th class="text-center py-2 sm:py-3 px-2 sm:px-3 md:px-4 text-xs sm:text-sm font-semibold text-[#005187]">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" class="border-b border-[#84b6f4]">
            <td colspan="5" class="py-10 text-center">
              <div class="flex items-center justify-center space-x-3">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-[#005187]"></div>
                <span class="text-[#4d82bc] font-medium">Cargando mediciones...</span>
              </div>
            </td>
          </tr>
          <tr v-else-if="mediciones.length === 0" class="border-b border-[#84b6f4]">
            <td colspan="5" class="py-10 text-center">
              <div class="text-[#4d82bc] mb-2">📭</div>
              <div class="text-[#4d82bc] font-medium">No hay mediciones disponibles</div>
            </td>
          </tr>
          <tr 
            v-else
            v-for="(medicion, index) in mediciones" 
            :key="medicion._id || index"
            class="border-b border-[#84b6f4] hover:bg-[#fcffff] transition-colors duration-150"
          >
            <td class="py-2 sm:py-3 px-2 sm:px-3 md:px-4 text-xs sm:text-sm font-medium text-[#005187]">
              {{ formatearFecha(medicion.fecha || medicion.timestamp) }}
            </td>
            <td class="py-2 sm:py-3 px-2 sm:px-3 md:px-4">
              <span 
                class="text-sm sm:text-lg font-semibold px-2 sm:px-3 py-1 rounded-md"
                :class="getNivelColor(medicion.distancia)"
              >
                {{ formatearNivel(medicion.distancia) }}
              </span>
            </td>
            <td class="py-2 sm:py-3 px-2 sm:px-3 md:px-4 hidden sm:table-cell">
              <span 
                class="px-2 sm:px-3 py-1 rounded-full text-xs font-medium"
                :class="getEstadoBadge(medicion.distancia)"
              >
                {{ getEstado(medicion.distancia) }}
              </span>
            </td>
            <td class="py-2 sm:py-3 px-2 sm:px-3 md:px-4 text-xs sm:text-sm font-medium text-[#4d82bc] hidden md:table-cell">
              {{ medicion.sensor_id || 'N/A' }}
            </td>
            <td class="py-2 sm:py-3 px-2 sm:px-3 md:px-4 text-center">
              <button 
                @click="verDetalle(medicion)"
                class="px-2 sm:px-3 py-1 sm:py-1.5 bg-[#4d82bc] text-white rounded-lg hover:bg-[#005187] transition-colors duration-150 text-xs font-medium whitespace-nowrap"
              >
                <span class="hidden sm:inline">Ver detalles</span>
                <span class="sm:hidden">Ver</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginación -->
    <div v-if="mediciones.length > 0" class="mt-4 sm:mt-5 md:mt-6 flex flex-col sm:flex-row items-start sm:items-center justify-between bg-[#c4dafa] rounded-lg p-3 sm:p-4 border border-[#84b6f4] gap-3">
      <div class="text-xs sm:text-sm font-medium text-[#005187]">
        Mostrando {{ Math.min(mediciones.length, limite) }} de {{ totalMediciones }} mediciones
      </div>
      <div class="flex space-x-2 w-full sm:w-auto">
        <button 
          @click="cargarMas"
          v-if="mediciones.length >= limite"
          class="w-full sm:w-auto px-4 py-2 bg-[#4d82bc] text-white rounded-lg hover:bg-[#005187] transition-colors duration-150 text-xs sm:text-sm font-medium"
        >
          Cargar más
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { obtenerMediciones } from '../services/medicionesService'

const mediciones = ref([])
const loading = ref(false)
const limite = ref(20)
const totalMediciones = ref(0)

function formatearFecha(fecha) {
  if (!fecha) return 'N/A'
  try {
    const date = new Date(fecha)
    return date.toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return 'Fecha inválida'
  }
}

function formatearNivel(distancia) {
  if (distancia === null || distancia === undefined || isNaN(distancia) || distancia < 0) {
    return 'Sin datos'
  }
  return `${distancia.toFixed(2)} cm`
}

function getNivelColor(distancia) {
  if (distancia === null || distancia === undefined || isNaN(distancia) || distancia < 0) {
    return 'text-[#4d82bc] bg-[#c4dafa]'
  }
  if (distancia <= 200) {
    return 'text-emerald-700 bg-emerald-50'
  } else if (distancia <= 400) {
    return 'text-amber-700 bg-amber-50'
  } else {
    return 'text-[#005187] bg-[#c4dafa]'
  }
}

function getEstado(distancia) {
  if (distancia === null || distancia === undefined || isNaN(distancia) || distancia < 0) {
    return 'Sin datos'
  }
  if (distancia <= 200) {
    return 'Normal'
  } else if (distancia <= 400) {
    return 'Alerta'
  } else {
    return 'Crítico'
  }
}

function getEstadoBadge(distancia) {
  if (distancia === null || distancia === undefined || isNaN(distancia) || distancia < 0) {
    return 'bg-[#c4dafa] text-[#4d82bc]'
  }
  if (distancia <= 200) {
    return 'bg-emerald-100 text-emerald-700'
  } else if (distancia <= 400) {
    return 'bg-amber-100 text-amber-700'
  } else {
    return 'bg-[#c4dafa] text-[#005187]'
  }
}

function verDetalle(medicion) {
  console.log('Ver detalle de medición:', medicion)
  // Aquí puedes implementar un modal o navegación a detalle
}

async function cargarMediciones() {
  loading.value = true
  try {
    const datos = await obtenerMediciones()
    if (Array.isArray(datos)) {
      mediciones.value = datos.slice(0, limite.value)
      totalMediciones.value = datos.length
    } else {
      mediciones.value = []
      totalMediciones.value = 0
    }
  } catch (error) {
    console.error('Error cargando mediciones:', error)
    mediciones.value = []
  } finally {
    loading.value = false
  }
}

function cargarMas() {
  limite.value += 20
  cargarMediciones()
}

onMounted(() => {
  cargarMediciones()
})
</script>

<style scoped>
.mediciones-table {
  margin-bottom: 2rem;
}
</style>
