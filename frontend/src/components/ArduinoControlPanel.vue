<template>
  <div class="arduino-control-panel bg-white rounded-xl shadow-lg p-6">
    <h3 class="text-xl font-bold text-gray-800 mb-4">
      🎛️ Control Arduino
    </h3>
    
    <!-- Estado de conexión -->
    <div class="mb-4 p-3 rounded-lg" :class="arduinoStore.isConnected ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
      <div class="flex items-center gap-2">
        <div :class="arduinoStore.isConnected ? 'bg-green-500' : 'bg-red-500'" class="w-3 h-3 rounded-full"></div>
        <span class="text-sm font-medium" :class="arduinoStore.isConnected ? 'text-green-700' : 'text-red-700'">
          {{ arduinoStore.isConnected ? 'Conectado' : 'Desconectado' }}
        </span>
      </div>
    </div>

    <!-- Controles -->
    <div class="grid grid-cols-2 gap-3">
      <!-- Buzzer ON -->
      <button
        @click="activarBuzzer"
        :disabled="arduinoStore.isLoading"
        class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <span v-if="arduinoStore.isLoading">⏳</span>
        <span v-else">🔊</span>
        Activar Buzzer
      </button>

      <!-- Buzzer OFF -->
      <button
        @click="desactivarBuzzer"
        :disabled="arduinoStore.isLoading"
        class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <span v-if="arduinoStore.isLoading">⏳</span>
        <span v-else">🔇</span>
        Apagar Buzzer
      </button>

      <!-- Estado -->
      <button
        @click="obtenerEstado"
        :disabled="arduinoStore.isLoading"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <span v-if="arduinoStore.isLoading">⏳</span>
        <span v-else">📊</span>
        Estado
      </button>

      <!-- Reset -->
      <button
        @click="reiniciarDispositivo"
        :disabled="arduinoStore.isLoading"
        class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <span v-if="arduinoStore.isLoading">⏳</span>
        <span v-else">🔄</span>
        Reset
      </button>
    </div>

    <!-- Historial de comandos -->
    <div v-if="arduinoStore.commandHistory.length > 0" class="mt-6">
      <h4 class="text-sm font-semibold text-gray-700 mb-2">Historial de comandos</h4>
      <div class="max-h-32 overflow-y-auto space-y-1">
        <div
          v-for="cmd in arduinoStore.commandHistory.slice(0, 5)"
          :key="cmd.id"
          class="text-xs p-2 bg-gray-50 rounded flex justify-between items-center"
        >
          <span class="font-mono">{{ cmd.command }}</span>
          <span class="text-gray-500">{{ formatTime(cmd.timestamp) }}</span>
        </div>
      </div>
      <button
        @click="arduinoStore.clearHistory"
        class="text-xs text-gray-500 hover:text-gray-700 mt-2"
      >
        Limpiar historial
      </button>
    </div>

    <!-- Último comando -->
    <div v-if="arduinoStore.lastCommand" class="mt-4 p-3 bg-blue-50 rounded-lg">
      <div class="text-sm">
        <span class="font-semibold">Último comando:</span>
        <span class="font-mono ml-2">{{ arduinoStore.lastCommand.command }}</span>
      </div>
      <div class="text-xs text-gray-600 mt-1">
        {{ formatTime(arduinoStore.lastCommand.timestamp) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { useArduinoStore } from '../stores/arduinoStore'

const arduinoStore = useArduinoStore()

const activarBuzzer = async () => {
  await arduinoStore.turnOnBuzzer('general', 1000)
}

const desactivarBuzzer = async () => {
  await arduinoStore.turnOffBuzzer()
}

const obtenerEstado = async () => {
  await arduinoStore.getDeviceStatus()
}

const reiniciarDispositivo = async () => {
  if (confirm('¿Estás seguro de que quieres reiniciar el dispositivo?')) {
    await arduinoStore.resetDevice()
  }
}

const formatTime = (timestamp) => {
  const now = new Date()
  const time = new Date(timestamp)
  const diff = Math.floor((now - time) / 1000)
  
  if (diff < 60) return `${diff}s`
  if (diff < 3600) return `${Math.floor(diff / 60)}m`
  return time.toLocaleTimeString()
}
</script>
