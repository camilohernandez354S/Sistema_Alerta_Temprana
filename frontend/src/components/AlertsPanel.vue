<template>
  <div class="alerts-panel bg-white rounded-xl shadow-lg p-6">
    <!-- Header del Panel -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">
        🚨 Sistema de Alertas
      </h2>
      <div class="flex gap-2">
        <button 
          @click="refrescarAlertas"
          :disabled="cargando"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          <span v-if="cargando">🔄</span>
          <span v-else>↻</span>
          Actualizar
        </button>
        <button 
          v-if="tieneAlertasActivas && esAdmin"
          @click="desactivarBuzzerGeneral"
          :disabled="procesandoBuzzer"
          class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
        >
          🔇 Silenciar Buzzer
        </button>
      </div>
    </div>

    <!-- Estado del Sistema -->
    <div class="mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Estado Actual -->
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="flex items-center gap-2">
            <div :class="getEstadoColor(estadoSistema.estado_actual)" class="w-4 h-4 rounded-full"></div>
            <h3 class="font-semibold text-gray-700">Estado Actual</h3>
          </div>
          <div class="mt-2">
            <div class="text-2xl font-bold" :class="getEstadoTextColor(estadoSistema.estado_actual)">
              {{ getEstadoTexto(estadoSistema.estado_actual) }}
            </div>
            <div class="text-sm text-gray-500">
              Nivel: {{ estadoSistema.nivel_actual }}cm
            </div>
          </div>
        </div>

        <!-- Alertas Activas -->
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded-full bg-orange-500"></div>
            <h3 class="font-semibold text-gray-700">Alertas Activas</h3>
          </div>
          <div class="mt-2">
            <div class="text-2xl font-bold text-orange-600">
              {{ estadoSistema.alertas_activas || 0 }}
            </div>
            <div class="text-sm text-gray-500">
              En el sistema
            </div>
          </div>
        </div>

        <!-- Estado del Buzzer -->
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="flex items-center gap-2">
            <div :class="estadoSistema.buzzer_activo ? 'bg-red-500 animate-pulse' : 'bg-green-500'" class="w-4 h-4 rounded-full"></div>
            <h3 class="font-semibold text-gray-700">Buzzer</h3>
          </div>
          <div class="mt-2">
            <div class="text-lg font-bold" :class="estadoSistema.buzzer_activo ? 'text-red-600' : 'text-green-600'">
              {{ estadoSistema.buzzer_activo ? '🔊 ACTIVO' : '🔇 Silencioso' }}
            </div>
            <div class="text-sm text-gray-500">
              {{ estadoSistema.buzzer_activo ? 'Alerta sonora' : 'Sin sonido' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="mb-4">
      <div class="flex gap-4 items-center">
        <label class="flex items-center gap-2">
          <input 
            type="checkbox" 
            v-model="filtros.soloActivas"
            @change="aplicarFiltros"
            class="rounded"
          >
          <span class="text-sm">Solo alertas activas</span>
        </label>
        <select 
          v-model="filtros.tipoAlerta"
          @change="aplicarFiltros"
          class="px-3 py-1 border rounded text-sm"
        >
          <option value="">Todos los tipos</option>
          <option value="inundacion">🌊 Inundación</option>
          <option value="sequia">🏜️ Sequía</option>
          <option value="normal">✅ Normal</option>
        </select>
      </div>
    </div>

    <!-- Lista de Alertas -->
    <div class="space-y-3">
      <div v-if="alertasFiltradas.length === 0" class="text-center py-8 text-gray-500">
        <div class="text-4xl mb-2">📭</div>
        <div>No hay alertas {{ filtros.soloActivas ? 'activas' : '' }}</div>
      </div>

      <div 
        v-for="alerta in alertasFiltradas" 
        :key="alerta._id"
        class="border rounded-lg p-4 transition-all duration-200"
        :class="getAlertaClases(alerta)"
      >
        <div class="flex justify-between items-start">
          <!-- Información de la Alerta -->
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <div class="text-2xl">{{ getAlertaIcono(alerta.tipo_alerta) }}</div>
              <div>
                <h3 class="font-semibold text-lg" :class="getAlertaTitleColor(alerta.tipo_alerta)">
                  {{ getAlertaTitulo(alerta.tipo_alerta) }}
                </h3>
                <div class="text-sm text-gray-600">
                  {{ formatearFecha(alerta.timestamp) }}
                </div>
              </div>
              <div v-if="alerta.alerta_activa" class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">
                ACTIVA
              </div>
              <div v-else class="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                INACTIVA
              </div>
            </div>

            <div class="text-gray-700 mb-2">
              {{ alerta.descripcion }}
            </div>

            <div class="flex gap-4 text-sm text-gray-500">
              <span>Nivel: <strong>{{ alerta.nivel_agua }}cm</strong></span>
              <span v-if="alerta.buzzer_activo" class="text-red-600">🔊 Buzzer activo</span>
              <span v-if="alerta.desactivada_por">
                Desactivada por: <strong>{{ alerta.desactivada_por }}</strong>
              </span>
            </div>
          </div>

          <!-- Acciones (Solo para Admins) -->
          <div v-if="esAdmin && alerta.alerta_activa" class="ml-4">
            <button 
              @click="desactivarAlerta(alerta._id)"
              :disabled="procesandoAlerta === alerta._id"
              class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50 text-sm"
            >
              <span v-if="procesandoAlerta === alerta._id">⏳</span>
              <span v-else">🛑</span>
              Desactivar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Paginación -->
    <div v-if="alertas.length >= filtros.limite" class="mt-6 text-center">
      <button 
        @click="cargarMasAlertas"
        :disabled="cargando"
        class="px-6 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:opacity-50"
      >
        Cargar más alertas
      </button>
    </div>

    <!-- Última Actualización -->
    <div class="mt-4 text-center text-xs text-gray-400">
      Última actualización: {{ ultimaActualizacion }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { getToken, getRol } from '../services/authService'

// Estado reactivo
const alertas = ref([])
const estadoSistema = ref({
  nivel_actual: 0,
  estado_actual: 'normal',
  alertas_activas: 0,
  buzzer_activo: false
})

const cargando = ref(false)
const procesandoAlerta = ref(null)
const procesandoBuzzer = ref(false)
const ultimaActualizacion = ref('')

// Filtros
const filtros = ref({
  soloActivas: true,
  tipoAlerta: '',
  limite: 20
})

// Configuración
const API_BASE_URL = 'http://localhost:5000'
const esAdmin = computed(() => getRol() === 'admin')
const tieneAlertasActivas = computed(() => estadoSistema.value.alertas_activas > 0)

// Alertas filtradas
const alertasFiltradas = computed(() => {
  let resultado = [...alertas.value]
  
  if (filtros.value.soloActivas) {
    resultado = resultado.filter(a => a.alerta_activa)
  }
  
  if (filtros.value.tipoAlerta) {
    resultado = resultado.filter(a => a.tipo_alerta === filtros.value.tipoAlerta)
  }
  
  return resultado
})

// Intervalo para actualización automática
let intervaloActualizacion = null

// Métodos
const obtenerHeaders = () => ({
  'Authorization': `Bearer ${getToken()}`,
  'Content-Type': 'application/json'
})

const cargarEstadoSistema = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/alertas/estado`, {
      headers: obtenerHeaders()
    })
    
    if (response.ok) {
      estadoSistema.value = await response.json()
    }
  } catch (error) {
    console.error('Error cargando estado del sistema:', error)
  }
}

const cargarAlertas = async () => {
  cargando.value = true
  try {
    const params = new URLSearchParams({
      activas: filtros.value.soloActivas.toString(),
      limite: filtros.value.limite.toString()
    })
    
    const response = await fetch(`${API_BASE_URL}/api/v1/alertas?${params}`, {
      headers: obtenerHeaders()
    })
    
    if (response.ok) {
      const data = await response.json()
      alertas.value = data.alertas || []
      ultimaActualizacion.value = new Date().toLocaleTimeString()
    } else {
      console.error('Error cargando alertas:', response.statusText)
    }
  } catch (error) {
    console.error('Error cargando alertas:', error)
  } finally {
    cargando.value = false
  }
}

const refrescarAlertas = async () => {
  await Promise.all([
    cargarEstadoSistema(),
    cargarAlertas()
  ])
}

const aplicarFiltros = () => {
  cargarAlertas()
}

const cargarMasAlertas = () => {
  filtros.value.limite += 20
  cargarAlertas()
}

const desactivarAlerta = async (alertaId) => {
  procesandoAlerta.value = alertaId
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/alertas/${alertaId}/desactivar`, {
      method: 'PATCH',
      headers: obtenerHeaders(),
      body: JSON.stringify({
        motivo: 'desactivacion_manual_admin_panel'
      })
    })
    
    if (response.ok) {
      await refrescarAlertas()
    } else {
      const error = await response.json()
      alert(`Error: ${error.error || 'No se pudo desactivar la alerta'}`)
    }
  } catch (error) {
    console.error('Error desactivando alerta:', error)
    alert('Error de conexión al desactivar la alerta')
  } finally {
    procesandoAlerta.value = null
  }
}

const desactivarBuzzerGeneral = async () => {
  procesandoBuzzer.value = true
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/alertas/buzzer/desactivar`, {
      method: 'POST',
      headers: obtenerHeaders()
    })
    
    if (response.ok) {
      await refrescarAlertas()
    } else {
      const error = await response.json()
      alert(`Error: ${error.error || 'No se pudo desactivar el buzzer'}`)
    }
  } catch (error) {
    console.error('Error desactivando buzzer:', error)
    alert('Error de conexión al desactivar el buzzer')
  } finally {
    procesandoBuzzer.value = false
  }
}

// Funciones de utilidad
const getEstadoColor = (estado) => {
  const colores = {
    'inundacion': 'bg-red-500',
    'sequia': 'bg-yellow-500',
    'normal': 'bg-green-500'
  }
  return colores[estado] || 'bg-gray-500'
}

const getEstadoTextColor = (estado) => {
  const colores = {
    'inundacion': 'text-red-600',
    'sequia': 'text-yellow-600',
    'normal': 'text-green-600'
  }
  return colores[estado] || 'text-gray-600'
}

const getEstadoTexto = (estado) => {
  const textos = {
    'inundacion': 'INUNDACIÓN',
    'sequia': 'SEQUÍA',
    'normal': 'NORMAL'
  }
  return textos[estado] || 'DESCONOCIDO'
}

const getAlertaIcono = (tipo) => {
  const iconos = {
    'inundacion': '🌊',
    'sequia': '🏜️',
    'normal': '✅'
  }
  return iconos[tipo] || '⚠️'
}

const getAlertaTitulo = (tipo) => {
  const titulos = {
    'inundacion': 'Alerta de Inundación',
    'sequia': 'Alerta de Sequía',
    'normal': 'Estado Normal'
  }
  return titulos[tipo] || 'Alerta Desconocida'
}

const getAlertaTitleColor = (tipo) => {
  const colores = {
    'inundacion': 'text-red-700',
    'sequia': 'text-yellow-700',
    'normal': 'text-green-700'
  }
  return colores[tipo] || 'text-gray-700'
}

const getAlertaClases = (alerta) => {
  const base = alerta.alerta_activa ? 'border-l-4 ' : 'border-l-2 opacity-75 '
  const colores = {
    'inundacion': 'border-red-500 bg-red-50',
    'sequia': 'border-yellow-500 bg-yellow-50',
    'normal': 'border-green-500 bg-green-50'
  }
  return base + (colores[alerta.tipo_alerta] || 'border-gray-500 bg-gray-50')
}

const formatearFecha = (timestamp) => {
  try {
    const fecha = new Date(timestamp)
    return fecha.toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Fecha inválida'
  }
}

// Lifecycle
onMounted(() => {
  refrescarAlertas()
  
  // Actualización automática cada 30 segundos
  intervaloActualizacion = setInterval(refrescarAlertas, 30000)
})

onUnmounted(() => {
  if (intervaloActualizacion) {
    clearInterval(intervaloActualizacion)
  }
})
</script>

<style scoped>
.alerts-panel {
  max-width: 100%;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
