<template>
  <div class="geospatial-map-container">
    <!-- Controles del mapa -->
    <div class="map-controls bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-4 mb-4">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Selector de radio -->
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700">Radio de búsqueda:</label>
          <select 
            v-model="selectedRadius" 
            @change="onRadiusChange"
            class="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="1000">1 km</option>
            <option value="2000">2 km</option>
            <option value="5000">5 km</option>
            <option value="10000">10 km</option>
            <option value="20000">20 km</option>
          </select>
        </div>

        <!-- Botón de ubicación actual -->
        <button
          @click="getCurrentLocation"
          :disabled="loading"
          class="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
          <span>Mi ubicación</span>
        </button>

        <!-- Botón de actualizar -->
        <button
          @click="refreshAlerts"
          :disabled="loading"
          class="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          <span>Actualizar</span>
        </button>

        <!-- Información de alertas -->
        <div class="flex items-center space-x-2 text-sm text-gray-600">
          <div class="w-3 h-3 bg-red-500 rounded-full"></div>
          <span>{{ alertsCount }} alertas</span>
        </div>
      </div>
    </div>

    <!-- Mapa -->
    <div class="map-wrapper bg-white rounded-lg shadow-lg overflow-hidden">
      <div 
        ref="mapContainer" 
        class="w-full h-96"
        :class="{ 'opacity-50': loading }"
      ></div>
      
      <!-- Overlay de carga -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm">
        <div class="text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-4 border-blue-200 border-t-blue-600 mx-auto mb-2"></div>
          <p class="text-sm text-gray-600">Cargando alertas...</p>
        </div>
      </div>
    </div>

    <!-- Lista de alertas -->
    <div v-if="alerts.length > 0" class="mt-4 bg-white rounded-lg shadow-lg p-4">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">Alertas en el área seleccionada</h3>
      <div class="space-y-2 max-h-64 overflow-y-auto">
        <div 
          v-for="alert in alerts" 
          :key="alert._id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center space-x-3">
            <div 
              class="w-4 h-4 rounded-full"
              :style="{ backgroundColor: getAlertColor(alert.estado) }"
            ></div>
            <div>
              <p class="font-medium text-gray-800">
                {{ alert.sensor_nombre || alert.sensor_id }}
              </p>
              <p class="text-sm text-gray-600">
                {{ alert.nivel }}cm - {{ alert.estado }}
              </p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-sm text-gray-500">
              {{ formatDistance(alert.distancia_km) }}
            </p>
            <p class="text-xs text-gray-400">
              {{ formatTime(alert.timestamp) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Mensaje cuando no hay alertas -->
    <div v-else-if="!loading && alerts.length === 0" class="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-center space-x-2">
        <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <p class="text-blue-800">No se encontraron alertas en el área seleccionada</p>
      </div>
    </div>

    <!-- Mensaje de error -->
    <div v-if="error" class="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center space-x-2">
        <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <p class="text-red-800">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { geospatialService } from '../services/geospatialService'

// Props
const props = defineProps({
  initialLat: {
    type: Number,
    default: -34.6037 // Buenos Aires por defecto
  },
  initialLng: {
    type: Number,
    default: -58.3816
  },
  initialZoom: {
    type: Number,
    default: 13
  }
})

// Estado reactivo
const mapContainer = ref(null)
const map = ref(null)
const selectedRadius = ref(5000)
const loading = ref(false)
const error = ref(null)
const alerts = ref([])
const alertsCount = ref(0)
const currentLocation = ref(null)

// Referencias para los marcadores y círculo
let markers = []
let radiusCircle = null

/**
 * Inicializar el mapa de Leaflet
 */
const initMap = async () => {
  if (!mapContainer.value) return

  try {
    // Crear mapa
    map.value = L.map(mapContainer.value).setView([props.initialLat, props.initialLng], props.initialZoom)

    // Agregar capa de tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map.value)

    // Evento de clic en el mapa
    map.value.on('click', (e) => {
      const { lat, lng } = e.latlng
      searchAlertsAtLocation(lat, lng)
    })

    console.log('✅ Mapa inicializado correctamente')

  } catch (err) {
    console.error('❌ Error inicializando mapa:', err)
    error.value = 'Error inicializando el mapa'
  }
}

/**
 * Obtener ubicación actual del usuario
 */
const getCurrentLocation = async () => {
  try {
    loading.value = true
    error.value = null

    const coords = await geospatialService.getCurrentLocation()
    currentLocation.value = coords

    // Centrar mapa en la ubicación actual
    map.value.setView([coords.lat, coords.lng], 15)

    // Buscar alertas en la ubicación actual
    await searchAlertsAtLocation(coords.lat, coords.lng)

  } catch (err) {
    console.error('❌ Error obteniendo ubicación:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

/**
 * Buscar alertas en una ubicación específica
 */
const searchAlertsAtLocation = async (lat, lng) => {
  try {
    loading.value = true
    error.value = null

    const result = await geospatialService.getAlertsInRadius(lat, lng, selectedRadius.value)
    
    alerts.value = result.alerts || []
    alertsCount.value = result.total || 0

    // Actualizar marcadores en el mapa
    updateMapMarkers(lat, lng)

  } catch (err) {
    console.error('❌ Error buscando alertas:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

/**
 * Actualizar marcadores en el mapa
 */
const updateMapMarkers = (centerLat, centerLng) => {
  // Limpiar marcadores existentes
  clearMarkers()

  // Agregar marcador del centro
  const centerMarker = L.marker([centerLat, centerLng], {
    icon: L.divIcon({
      className: 'center-marker',
      html: '<div class="w-4 h-4 bg-blue-600 rounded-full border-2 border-white shadow-lg"></div>',
      iconSize: [16, 16]
    })
  }).addTo(map.value)

  centerMarker.bindPopup(`
    <div class="text-center">
      <p class="font-semibold">Centro de búsqueda</p>
      <p class="text-sm text-gray-600">${centerLat.toFixed(4)}, ${centerLng.toFixed(4)}</p>
      <p class="text-sm text-gray-600">Radio: ${geospatialService.formatRadius(selectedRadius.value)}</p>
    </div>
  `)

  markers.push(centerMarker)

  // Agregar marcadores de alertas
  alerts.value.forEach(alert => {
    const coords = alert.location.coordinates
    const lat = coords[1]
    const lng = coords[0]

    const alertIcon = L.divIcon({
      className: 'alert-marker',
      html: `
        <div class="w-6 h-6 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-white text-xs font-bold"
             style="background-color: ${getAlertColor(alert.estado)}">
          ${getAlertEmoji(alert.estado)}
        </div>
      `,
      iconSize: [24, 24]
    })

    const marker = L.marker([lat, lng], { icon: alertIcon }).addTo(map.value)
    
    marker.bindPopup(`
      <div class="min-w-48">
        <h3 class="font-semibold text-gray-800 mb-2">
          ${alert.sensor_nombre || alert.sensor_id}
        </h3>
        <div class="space-y-1 text-sm">
          <p><span class="font-medium">Estado:</span> ${alert.estado}</p>
          <p><span class="font-medium">Nivel:</span> ${alert.nivel} cm</p>
          <p><span class="font-medium">Distancia:</span> ${formatDistance(alert.distancia_km)}</p>
          <p><span class="font-medium">Hora:</span> ${formatTime(alert.timestamp)}</p>
        </div>
      </div>
    `)

    markers.push(marker)
  })

  // Agregar círculo de radio
  radiusCircle = L.circle([centerLat, centerLng], {
    radius: selectedRadius.value,
    color: '#3b82f6',
    fillColor: '#3b82f6',
    fillOpacity: 0.1,
    weight: 2
  }).addTo(map.value)

  // Ajustar vista para mostrar todos los marcadores
  if (alerts.value.length > 0) {
    const group = new L.featureGroup(markers)
    map.value.fitBounds(group.getBounds().pad(0.1))
  }
}

/**
 * Limpiar marcadores del mapa
 */
const clearMarkers = () => {
  markers.forEach(marker => map.value.removeLayer(marker))
  markers = []
  
  if (radiusCircle) {
    map.value.removeLayer(radiusCircle)
    radiusCircle = null
  }
}

/**
 * Manejar cambio de radio
 */
const onRadiusChange = () => {
  if (currentLocation.value) {
    searchAlertsAtLocation(currentLocation.value.lat, currentLocation.value.lng)
  }
}

/**
 * Actualizar alertas
 */
const refreshAlerts = () => {
  if (currentLocation.value) {
    searchAlertsAtLocation(currentLocation.value.lat, currentLocation.value.lng)
  }
}

/**
 * Obtener color de alerta
 */
const getAlertColor = (estado) => {
  return geospatialService.getAlertColor(estado)
}

/**
 * Obtener emoji de alerta
 */
const getAlertEmoji = (estado) => {
  switch (estado) {
    case 'inundacion':
      return '💧'
    case 'sequia':
      return '☀️'
    case 'normal':
      return '✅'
    default:
      return '⚠️'
  }
}

/**
 * Formatear distancia
 */
const formatDistance = (km) => {
  if (km < 1) {
    return `${Math.round(km * 1000)}m`
  }
  return `${km.toFixed(1)}km`
}

/**
 * Formatear tiempo
 */
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Intervalo de actualización automática
let refreshInterval = null

// Lifecycle hooks
onMounted(async () => {
  await nextTick()
  await initMap()
  
  // Buscar alertas en la ubicación inicial
  await searchAlertsAtLocation(props.initialLat, props.initialLng)
  
  // Configurar actualización automática cada 30 segundos
  refreshInterval = setInterval(() => {
    if (currentLocation.value) {
      searchAlertsAtLocation(currentLocation.value.lat, currentLocation.value.lng)
    }
  }, 30000) // 30 segundos
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
  
  // Limpiar intervalo de actualización
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

// Watchers
watch(() => props.initialLat, (newLat) => {
  if (map.value) {
    map.value.setView([newLat, props.initialLng], props.initialZoom)
  }
})

watch(() => props.initialLng, (newLng) => {
  if (map.value) {
    map.value.setView([props.initialLat, newLng], props.initialZoom)
  }
})
</script>

<style>
.geospatial-map-container {
  width: 100%;
}

.map-wrapper {
  position: relative;
}

/* Estilos para marcadores personalizados */
.center-marker {
  z-index: 10;
}

.alert-marker {
  z-index: 20;
}

/* Estilos para popups de Leaflet */
.leaflet-popup-content {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.leaflet-popup-content-wrapper {
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>
