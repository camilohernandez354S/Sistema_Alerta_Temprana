<template>
  <div class="toast-container fixed top-4 right-4 z-50 space-y-2">
    <TransitionGroup
      name="toast"
      tag="div"
      class="space-y-2"
    >
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="getToastClasses(notification.type)"
        class="toast-notification max-w-sm w-full shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden"
      >
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <component :is="getIcon(notification.type)" class="h-5 w-5" />
            </div>
            <div class="ml-3 w-0 flex-1 pt-0.5">
              <p class="text-sm font-medium text-white">
                {{ notification.message }}
              </p>
              <p class="text-xs text-white/80 mt-1">
                {{ formatTime(notification.timestamp) }}
              </p>
            </div>
            <div class="ml-4 flex-shrink-0 flex">
              <button
                @click="removeNotification(notification.id)"
                class="bg-transparent rounded-md inline-flex text-white hover:text-white/80 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white/50"
              >
                <span class="sr-only">Cerrar</span>
                <XMarkIcon class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useArduinoStore } from '../stores/arduinoStore'
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  InformationCircleIcon, 
  ExclamationTriangleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const arduinoStore = useArduinoStore()

const notifications = computed(() => arduinoStore.notifications)

const getToastClasses = (type) => {
  const baseClasses = 'transform transition-all duration-300 ease-in-out'
  
  const typeClasses = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500'
  }
  
  return `${baseClasses} ${typeClasses[type] || typeClasses.info}`
}

const getIcon = (type) => {
  const icons = {
    success: CheckCircleIcon,
    error: XCircleIcon,
    warning: ExclamationTriangleIcon,
    info: InformationCircleIcon
  }
  
  return icons[type] || icons.info
}

const formatTime = (timestamp) => {
  const now = new Date()
  const time = new Date(timestamp)
  const diff = now - time
  
  if (diff < 1000) return 'Ahora'
  if (diff < 60000) return `${Math.floor(diff / 1000)}s`
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m`
  return time.toLocaleTimeString()
}

const removeNotification = (id) => {
  arduinoStore.removeNotification(id)
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
