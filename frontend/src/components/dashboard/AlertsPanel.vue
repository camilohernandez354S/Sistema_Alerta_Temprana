<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">
        <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
        Alertas Activas
      </h2>
      <div class="flex items-center space-x-2">
        <button 
          @click="refreshAlertas" 
          :disabled="loading"
          class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors duration-200"
        >
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': loading }"></i>
          <span>Actualizar</span>
        </button>
        <span class="text-sm text-gray-500">
          Total: {{ alertas.length }}
        </span>
      </div>
    </div>

    <!-- Estado de carga -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <div class="flex items-center">
        <i class="fas fa-exclamation-circle text-red-500 mr-2"></i>
        <span class="text-red-700">{{ error }}</span>
      </div>
    </div>

    <!-- Lista vacía -->
    <div v-else-if="alertas.length === 0" class="text-center py-12">
      <i class="fas fa-check-circle text-green-500 text-4xl mb-4"></i>
      <p class="text-gray-600 text-lg">No hay alertas activas</p>
      <p class="text-gray-400 text-sm">El sistema está funcionando normalmente</p>
    </div>

    <!-- Lista de alertas -->
    <div v-else class="space-y-4">
      <div 
        v-for="alerta in alertas" 
        :key="alerta._id"
        class="border rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
        :class="getAlertCardClass(alerta.tipo)"
      >
        <div class="flex items-start justify-between">
          <!-- Información de la alerta -->
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-2">
              <!-- Icono y tipo -->
              <div class="flex items-center space-x-2">
                <i :class="getAlertIcon(alerta.tipo)" class="text-lg"></i>
                <span class="font-semibold text-lg" :class="getAlertTextColor(alerta.tipo)">
                  {{ getAlertTypeLabel(alerta.tipo) }}
                </span>
              </div>
              
              <!-- Badge de estado -->
              <span 
                class="px-2 py-1 rounded-full text-xs font-medium"
                :class="getStatusBadgeClass(alerta.estado_resolucion || 'Activa')"
              >
                {{ alerta.estado_resolucion || 'Activa' }}
              </span>
            </div>

            <!-- Detalles -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
              <div class="flex items-center space-x-2">
                <i class="fas fa-water text-blue-500"></i>
                <span>
                  <strong>Nivel:</strong> {{ alerta.nivel_agua }} cm
                </span>
              </div>
              
              <div class="flex items-center space-x-2">
                <i class="fas fa-clock text-gray-500"></i>
                <span>
                  <strong>Hora:</strong> {{ formatearFecha(alerta.timestamp) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Botones de acción -->
          <div 
            v-if="!alerta.estado_resolucion || alerta.estado_resolucion === 'Activa'"
            class="flex flex-col space-y-2 ml-4"
          >
            <button
              @click="procesarResolverAlerta(alerta._id)"
              :disabled="procesandoAccion === alerta._id"
              class="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-xs font-medium transition-colors duration-200 flex items-center space-x-1"
            >
              <i class="fas fa-check" :class="{ 'animate-spin': procesandoAccion === alerta._id }"></i>
              <span>Resolver</span>
            </button>
            
            <button
              @click="procesarDescartarAlerta(alerta._id)"
              :disabled="procesandoAccion === alerta._id"
              class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-xs font-medium transition-colors duration-200 flex items-center space-x-1"
            >
              <i class="fas fa-times" :class="{ 'animate-spin': procesandoAccion === alerta._id }"></i>
              <span>Descartar</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Paginación simple -->
    <div v-if="alertas.length > 0" class="mt-6 flex justify-center">
      <button
        @click="cargarMasAlertas"
        :disabled="loading"
        class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors duration-200"
      >
        Cargar más alertas
      </button>
    </div>
  </div>
</template>

<script>
import { 
  obtenerAlertas, 
  resolverAlerta, 
  descartarAlerta, 
  formatearFechaAlerta,
  obtenerEstilosAlerta,
  obtenerEtiquetaTipoAlerta,
  obtenerEstilosEstado
} from '../../services/alertasService.js'

export default {
  name: 'AlertsPanel',
  data() {
    return {
      alertas: [],
      loading: false,
      error: null,
      procesandoAccion: null,
      limite: 10
    }
  },
  mounted() {
    this.cargarAlertas()
    // Actualizar alertas cada 30 segundos
    this.interval = setInterval(() => {
      this.cargarAlertas(false) // Sin mostrar loading
    }, 30000)
  },
  beforeUnmount() {
    if (this.interval) {
      clearInterval(this.interval)
    }
  },
  methods: {
    async cargarAlertas(mostrarLoading = true) {
      if (mostrarLoading) {
        this.loading = true
      }
      this.error = null
      
      try {
        const data = await obtenerAlertas(this.limite)
        this.alertas = data.alertas || []
        
      } catch (err) {
        this.error = err.message
        console.error('Error cargando alertas:', err)
      } finally {
        this.loading = false
      }
    },

    async refreshAlertas() {
      await this.cargarAlertas()
    },

    async cargarMasAlertas() {
      this.limite += 10
      await this.cargarAlertas()
    },

    async procesarResolverAlerta(alertaId) {
      await this.procesarAccionAlerta(alertaId, 'resolver')
    },

    async procesarDescartarAlerta(alertaId) {
      await this.procesarAccionAlerta(alertaId, 'descartar')
    },

    async procesarAccionAlerta(alertaId, accion) {
      this.procesandoAccion = alertaId
      
      try {
        // Llamar al servicio correspondiente
        if (accion === 'resolver') {
          await resolverAlerta(alertaId)
        } else {
          await descartarAlerta(alertaId)
        }
        
        // Actualizar estado local
        const alertaIndex = this.alertas.findIndex(a => a._id === alertaId)
        if (alertaIndex !== -1) {
          this.alertas[alertaIndex].estado_resolucion = accion === 'resolver' ? 'Resuelta' : 'Descartada'
        }
        
        // Emitir evento de éxito
        this.$emit('alerta-procesada', { 
          id: alertaId, 
          accion, 
          mensaje: `Alerta ${accion === 'resolver' ? 'resuelta' : 'descartada'} exitosamente` 
        })
        
      } catch (err) {
        this.error = err.message
        console.error(`Error al ${accion} alerta:`, err)
      } finally {
        this.procesandoAccion = null
      }
    },

    getAlertTypeLabel(tipo) {
      return obtenerEtiquetaTipoAlerta(tipo)
    },

    getAlertIcon(tipo) {
      return obtenerEstilosAlerta(tipo).icon
    },

    getAlertTextColor(tipo) {
      return obtenerEstilosAlerta(tipo).textColor
    },

    getAlertCardClass(tipo) {
      return obtenerEstilosAlerta(tipo).cardClass
    },

    getStatusBadgeClass(estado) {
      return obtenerEstilosEstado(estado)
    },

    formatearFecha(timestamp) {
      return formatearFechaAlerta(timestamp)
    }
  }
}
</script>

<style scoped>
/* Estilos adicionales si es necesario */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Transiciones suaves */
.transition-colors {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

.transition-shadow {
  transition-property: box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
