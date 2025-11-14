/**
 * Configuración centralizada de la API
 * Lee la configuración del servidor desde el endpoint /api/config
 * que obtiene los valores del .env del backend (SERVER_IP, SERVER_PORT, etc.)
 */

// Variable global para almacenar la configuración del servidor
let serverConfig = null
let configLoadPromise = null

/**
 * Obtener configuración del servidor desde el backend
 * El backend lee el .env y devuelve SERVER_IP, SERVER_PORT, FLASK_SERVER_URL
 */
async function loadServerConfig() {
  if (serverConfig) {
    return serverConfig
  }
  
  if (configLoadPromise) {
    return configLoadPromise
  }
  
  configLoadPromise = (async () => {
    try {
      // Detectar URL base inicial desde el navegador
      const hostname = window.location.hostname
      const protocol = window.location.protocol
      const initialBaseUrl = (hostname === 'localhost' || hostname === '127.0.0.1') 
        ? 'http://localhost:5000'
        : `${protocol}//${hostname}:5000`
      
      // Intentar obtener configuración del backend (lee del .env)
      const response = await fetch(`${initialBaseUrl}/api/config`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        const config = await response.json()
        serverConfig = {
          apiBaseUrl: config.flask_server_url || `http://${config.server_ip}:${config.server_port}`,
          serverIp: config.server_ip,
          serverPort: config.server_port,
          frontendPort: config.frontend_port
        }
        console.log('✅ Configuración cargada desde .env:', serverConfig)
        return serverConfig
      }
    } catch (error) {
      console.warn('⚠️ No se pudo obtener configuración del servidor, usando detección automática:', error)
    }
    
    // Fallback: usar detección automática
    const hostname = window.location.hostname
    const protocol = window.location.protocol
    
    serverConfig = {
      apiBaseUrl: (hostname === 'localhost' || hostname === '127.0.0.1')
        ? 'http://localhost:5000'
        : `${protocol}//${hostname}:5000`,
      serverIp: hostname,
      serverPort: '5000',
      frontendPort: '8080'
    }
    
    return serverConfig
  })()
  
  return configLoadPromise
}

/**
 * Obtener URL base de la API
 * Intenta usar la configuración del servidor (del .env), 
 * si no está disponible usa detección automática
 */
function getApiBaseUrl() {
  // En producción, usar VITE_API_URL si está definido
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // Si ya tenemos la configuración del servidor, usarla
  if (serverConfig) {
    return serverConfig.apiBaseUrl
  }
  
  // Fallback: detección automática desde el navegador
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname
    const protocol = window.location.protocol
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:5000'
    }
    
    return `${protocol}//${hostname}:5000`
  }
  
  return 'http://localhost:5000'
}

// Cargar configuración del servidor al iniciar (en segundo plano)
if (typeof window !== 'undefined') {
  loadServerConfig().catch(err => {
    console.warn('Error al cargar configuración:', err)
  })
}

// URL base inicial (se actualizará cuando se cargue la configuración)
const API_BASE_URL = getApiBaseUrl()

/**
 * Obtener URL base de forma dinámica (espera a que se cargue la configuración si es necesario)
 * Esta función puede ser usada por servicios que necesitan la URL correcta del .env
 */
export async function getApiBaseUrlAsync() {
  await loadServerConfig()
  return getApiBaseUrl()
}

// URL completa para endpoints de API (usa detección automática inicialmente)
export const API_URL = `${API_BASE_URL}/api`

// URL para endpoints de sensor
export const SENSOR_API_URL = `${API_BASE_URL}/api/sensor`

// Exportar función para obtener configuración del servidor
export { loadServerConfig }

// Exportar URL base para casos especiales
export default API_BASE_URL

