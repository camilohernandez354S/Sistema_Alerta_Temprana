<template>
  <div class="semaforo-container">
    <div class="semaforo-box">
      <h3 class="text-lg font-semibold text-gray-800 mb-4 text-center">
        🚦 Semáforo de Estado
      </h3>
      
      <!-- Semáforo visual -->
      <div class="semaforo">
        <!-- Luz Roja (Inundación) -->
        <div 
          class="semaforo-luz semaforo-rojo"
          :class="{ 'activo': estado === 'Inundación', 'parpadeando': estado === 'Inundación' && parpadeando }"
        >
          <div class="luz-interna"></div>
        </div>
        
        <!-- Luz Amarilla (Normal) -->
        <div 
          class="semaforo-luz semaforo-amarillo"
          :class="{ 'activo': estado === 'Normal' }"
        >
          <div class="luz-interna"></div>
        </div>
        
        <!-- Luz Verde (Sequía) -->
        <div 
          class="semaforo-luz semaforo-verde"
          :class="{ 'activo': estado === 'Sequía' }"
        >
          <div class="luz-interna"></div>
        </div>
      </div>
      
      <!-- Estado actual -->
      <div class="mt-4 text-center">
        <div class="text-2xl font-bold" :class="getEstadoColorClass(estado)">
          {{ estado || 'Sin datos' }}
        </div>
        <div v-if="nivel !== null" class="text-sm text-gray-600 mt-1">
          Nivel: {{ nivel.toFixed(2) }} cm
        </div>
        <div v-if="ultimaActualizacion" class="text-xs text-gray-500 mt-1">
          Actualizado: {{ formatTime(ultimaActualizacion) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  estado: {
    type: String,
    default: null
  },
  nivel: {
    type: Number,
    default: null
  },
  ultimaActualizacion: {
    type: String,
    default: null
  }
})

const parpadeando = ref(false)
let parpadeoInterval = null

const getEstadoColorClass = (estado) => {
  switch (estado) {
    case 'Inundación':
      return 'text-red-600'
    case 'Sequía':
      return 'text-orange-600'
    case 'Normal':
      return 'text-green-600'
    default:
      return 'text-gray-600'
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return 'N/A'
  try {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (e) {
    return 'N/A'
  }
}

// Efecto de parpadeo para inundación
onMounted(() => {
  if (props.estado === 'Inundación') {
    parpadeoInterval = setInterval(() => {
      parpadeando.value = !parpadeando.value
    }, 500)
  }
})

onUnmounted(() => {
  if (parpadeoInterval) {
    clearInterval(parpadeoInterval)
  }
})

// Watch para estado y actualizar parpadeo
import { watch } from 'vue'
watch(() => props.estado, (newEstado) => {
  if (parpadeoInterval) {
    clearInterval(parpadeoInterval)
    parpadeoInterval = null
  }
  
  if (newEstado === 'Inundación') {
    parpadeoInterval = setInterval(() => {
      parpadeando.value = !parpadeando.value
    }, 500)
  } else {
    parpadeando.value = false
  }
})
</script>

<style scoped>
.semaforo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

.semaforo-box {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 2px solid #e5e7eb;
  width: 100%;
  max-width: 300px;
}

.semaforo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

.semaforo-luz {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #374151;
  border: 4px solid #1f2937;
  position: relative;
  transition: all 0.3s ease;
  box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.5);
}

.semaforo-luz .luz-interna {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  opacity: 0.3;
  transition: opacity 0.3s ease;
}

.semaforo-rojo .luz-interna {
  background: radial-gradient(circle at 30% 30%, #ef4444, #dc2626, #991b1b);
}

.semaforo-amarillo .luz-interna {
  background: radial-gradient(circle at 30% 30%, #fbbf24, #f59e0b, #d97706);
}

.semaforo-verde .luz-interna {
  background: radial-gradient(circle at 30% 30%, #10b981, #059669, #047857);
}

/* Estado activo */
.semaforo-luz.activo {
  box-shadow: 
    0 0 20px rgba(255, 255, 255, 0.5),
    inset 0 0 20px rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: scale(1.1);
}

.semaforo-luz.activo .luz-interna {
  opacity: 1;
}

/* Parpadeo para inundación */
.semaforo-luz.parpadeando {
  animation: parpadeo 0.5s infinite;
}

@keyframes parpadeo {
  0%, 100% {
    opacity: 1;
    transform: scale(1.1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.05);
  }
}

/* Efecto de brillo cuando está activo */
.semaforo-luz.activo::before {
  content: '';
  position: absolute;
  top: 20%;
  left: 25%;
  width: 30%;
  height: 30%;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  filter: blur(8px);
}

/* Estado inactivo */
.semaforo-luz:not(.activo) {
  opacity: 0.4;
}
</style>

