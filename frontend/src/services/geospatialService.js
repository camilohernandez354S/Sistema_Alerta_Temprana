/**
 * Servicio para operaciones geoespaciales en el frontend
 * Maneja la comunicación con el backend para alertas georreferenciadas
 * Principio SRP: Responsabilidad única de manejar datos geoespaciales
 */
import { ref } from 'vue'
import { API_URL } from '../config/api.js'

// Estado reactivo global para alertas geoespaciales
const alerts = ref([])
const loading = ref(false)
const error = ref(null)
const currentLocation = ref(null)
const selectedRadius = ref(5000) // Radio por defecto: 5km

class GeospatialService {
  constructor() {
    this.baseURL = API_URL
    this.token = localStorage.getItem('token')
  }

  /**
   * Actualizar token de autenticación
   */
  updateToken(token) {
    this.token = token
  }

  /**
   * Obtener headers de autenticación
   */
  getAuthHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.token}`
    }
  }

  /**
   * Obtener alertas dentro de un radio específico
   * @param {number} lat - Latitud
   * @param {number} lng - Longitud
   * @param {number} radius - Radio en metros
   * @returns {Promise<Object>} - Resultado de la consulta
   */
  async getAlertsInRadius(lat, lng, radius = 5000) {
    try {
      loading.value = true
      error.value = null

      const url = `${this.baseURL}/alertas?lat=${lat}&lng=${lng}&radio=${radius}`
      
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `Error HTTP: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.success) {
        alerts.value = data.alerts || []
        currentLocation.value = { lat, lng }
        selectedRadius.value = radius
        
        console.log(`✅ ${data.total} alertas encontradas en radio de ${radius}m`)
        return data
      } else {
        throw new Error(data.error || 'Error obteniendo alertas')
      }

    } catch (err) {
      console.error('❌ Error obteniendo alertas geoespaciales:', err)
      error.value = err.message
      alerts.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Obtener todos los sensores registrados
   * @returns {Promise<Object>} - Lista de sensores
   */
  async getSensors() {
    try {
      const url = `${this.baseURL}/sensores`
      
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `Error HTTP: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.success) {
        console.log(`✅ ${data.total} sensores obtenidos`)
        return data.sensors || []
      } else {
        throw new Error(data.error || 'Error obteniendo sensores')
      }

    } catch (err) {
      console.error('❌ Error obteniendo sensores:', err)
      throw err
    }
  }

  /**
   * Crear o actualizar un sensor con ubicación
   * @param {Object} sensorData - Datos del sensor
   * @returns {Promise<Object>} - Resultado de la operación
   */
  async createSensor(sensorData) {
    try {
      const url = `${this.baseURL}/sensores`
      
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(sensorData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `Error HTTP: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.success) {
        console.log(`✅ Sensor ${data.sensor_id} ${data.operation} exitosamente`)
        return data
      } else {
        throw new Error(data.error || 'Error creando sensor')
      }

    } catch (err) {
      console.error('❌ Error creando sensor:', err)
      throw err
    }
  }

  /**
   * Guardar medición con datos geoespaciales
   * @param {Object} measurementData - Datos de la medición
   * @returns {Promise<Object>} - Resultado de la operación
   */
  async saveMeasurement(measurementData) {
    try {
      const url = `${this.baseURL}/mediciones`
      
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(measurementData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `Error HTTP: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.success) {
        console.log(`✅ Medición guardada: ${data.nivel}cm en ${data.sensor_id}`)
        return data
      } else {
        throw new Error(data.error || 'Error guardando medición')
      }

    } catch (err) {
      console.error('❌ Error guardando medición:', err)
      throw err
    }
  }

  /**
   * Obtener ubicación actual del usuario usando geolocalización del navegador
   * @returns {Promise<Object>} - Coordenadas del usuario
   */
  async getCurrentLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocalización no soportada por este navegador'))
        return
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy
          }
          console.log('📍 Ubicación obtenida:', coords)
          resolve(coords)
        },
        (error) => {
          let errorMessage = 'Error obteniendo ubicación'
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Permiso de ubicación denegado'
              break
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Ubicación no disponible'
              break
            case error.TIMEOUT:
              errorMessage = 'Tiempo de espera agotado'
              break
          }
          console.error('❌ Error geolocalización:', errorMessage)
          reject(new Error(errorMessage))
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // 5 minutos
        }
      )
    })
  }

  /**
   * Calcular distancia entre dos puntos usando fórmula de Haversine
   * @param {number} lat1 - Latitud punto 1
   * @param {number} lng1 - Longitud punto 1
   * @param {number} lat2 - Latitud punto 2
   * @param {number} lng2 - Longitud punto 2
   * @returns {number} - Distancia en kilómetros
   */
  calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371 // Radio de la Tierra en kilómetros
    const dLat = this.toRadians(lat2 - lat1)
    const dLng = this.toRadians(lng2 - lng1)
    
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
              Math.sin(dLng / 2) * Math.sin(dLng / 2)
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }

  /**
   * Convertir grados a radianes
   * @param {number} degrees - Grados
   * @returns {number} - Radianes
   */
  toRadians(degrees) {
    return degrees * (Math.PI / 180)
  }

  /**
   * Formatear radio para mostrar en la interfaz
   * @param {number} meters - Radio en metros
   * @returns {string} - Radio formateado
   */
  formatRadius(meters) {
    if (meters >= 1000) {
      return `${(meters / 1000).toFixed(1)} km`
    }
    return `${meters} m`
  }

  /**
   * Obtener color del marcador según el estado de la alerta
   * @param {string} estado - Estado de la alerta
   * @returns {string} - Color en formato hexadecimal
   */
  getAlertColor(estado) {
    switch (estado) {
      case 'inundacion':
        return '#ef4444' // rojo
      case 'sequia':
        return '#f59e0b' // naranja
      case 'normal':
        return '#10b981' // verde
      default:
        return '#6b7280' // gris
    }
  }

  /**
   * Obtener icono según el estado de la alerta
   * @param {string} estado - Estado de la alerta
   * @returns {string} - Nombre del icono
   */
  getAlertIcon(estado) {
    switch (estado) {
      case 'inundacion':
        return 'droplets'
      case 'sequia':
        return 'sun'
      case 'normal':
        return 'check-circle'
      default:
        return 'alert-circle'
    }
  }
}

// Crear instancia del servicio
const geospatialService = new GeospatialService()

// Exportar servicio y estado reactivo
export { geospatialService, alerts, loading, error, currentLocation, selectedRadius }
export default geospatialService
