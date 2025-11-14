import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import API_BASE_URL from '../config/api.js'

export const useArduinoStore = defineStore('arduino', () => {
  // Estado reactivo
  const isLoading = ref(false)
  const lastCommand = ref(null)
  const commandHistory = ref([])
  const connectionStatus = ref(false)
  const notifications = ref([])

  // Getters
  const isConnected = computed(() => connectionStatus.value)
  const hasRecentCommand = computed(() => {
    if (!lastCommand.value) return false
    const now = new Date()
    const commandTime = new Date(lastCommand.value.timestamp)
    return (now - commandTime) < 30000 // 30 segundos
  })

  // Funciones de utilidad
  const getAuthHeaders = () => {
    const token = localStorage.getItem('token')
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  }

  const addNotification = (type, message) => {
    const notification = {
      id: Date.now(),
      type, // 'success', 'error', 'info', 'warning'
      message,
      timestamp: new Date()
    }
    notifications.value.unshift(notification)
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      removeNotification(notification.id)
    }, 5000)
  }

  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  // Función genérica para enviar comandos
  const sendCommand = async (command, parameters = {}) => {
    isLoading.value = true
    lastCommand.value = null

    try {
      const payload = {
        comando: command,
        ...(Object.keys(parameters).length > 0 && { parametros: parameters })
      }

      console.log('📤 Enviando comando:', payload)

      const response = await fetch(`${API_BASE_URL}/api/mediciones/comando`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      })

      const result = await response.json()

      if (response.ok && result.status === 'success') {
        lastCommand.value = {
          command,
          timestamp: new Date(),
          result
        }
        
        commandHistory.value.unshift({
          id: Date.now(),
          command,
          parameters,
          result,
          timestamp: new Date()
        })

        // Limitar historial a 50 comandos
        if (commandHistory.value.length > 50) {
          commandHistory.value = commandHistory.value.slice(0, 50)
        }

        addNotification('success', `✅ ${getCommandMessage(command, 'success')}`)
        connectionStatus.value = true
        
        return {
          success: true,
          data: result,
          message: result.message
        }
      } else {
        const errorMessage = result.message || result.error || 'Error desconocido'
        addNotification('error', `❌ ${getCommandMessage(command, 'error')}: ${errorMessage}`)
        connectionStatus.value = false
        
        return {
          success: false,
          error: errorMessage,
          data: result
        }
      }
    } catch (error) {
      console.error('Error enviando comando:', error)
      const errorMessage = 'Error de conexión al enviar comando'
      addNotification('error', `❌ ${errorMessage}`)
      connectionStatus.value = false
      
      return {
        success: false,
        error: errorMessage
      }
    } finally {
      isLoading.value = false
    }
  }

  // Funciones específicas para comandos comunes
  const turnOffBuzzer = async () => {
    return await sendCommand('BUZZER_OFF')
  }

  const turnOnBuzzer = async (alertType = 'general', frequency = null) => {
    const parameters = { alert_type: alertType }
    if (frequency) {
      parameters.frequency = frequency
    }
    return await sendCommand('BUZZER_ON', parameters)
  }

  const resetDevice = async () => {
    return await sendCommand('RESET')
  }

  const getDeviceStatus = async () => {
    return await sendCommand('STATUS')
  }

  // Función para obtener mensajes de comando
  const getCommandMessage = (command, type) => {
    const messages = {
      BUZZER_OFF: {
        success: 'Buzzer apagado remotamente',
        error: 'Error al apagar buzzer'
      },
      BUZZER_ON: {
        success: 'Buzzer activado remotamente',
        error: 'Error al activar buzzer'
      },
      RESET: {
        success: 'Dispositivo reiniciado',
        error: 'Error al reiniciar dispositivo'
      },
      STATUS: {
        success: 'Estado del dispositivo obtenido',
        error: 'Error al obtener estado'
      }
    }
    
    return messages[command]?.[type] || `Comando ${command} ${type === 'success' ? 'ejecutado' : 'falló'}`
  }

  // Función para limpiar historial
  const clearHistory = () => {
    commandHistory.value = []
  }

  // Función para limpiar notificaciones
  const clearNotifications = () => {
    notifications.value = []
  }

  return {
    // Estado
    isLoading,
    lastCommand,
    commandHistory,
    connectionStatus,
    notifications,
    
    // Getters
    isConnected,
    hasRecentCommand,
    
    // Acciones
    sendCommand,
    turnOffBuzzer,
    turnOnBuzzer,
    resetDevice,
    getDeviceStatus,
    addNotification,
    removeNotification,
    clearHistory,
    clearNotifications
  }
})
