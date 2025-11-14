/**
 * Configuración centralizada de la API
 * Usa variables de entorno de Vite para flexibilidad entre desarrollo y producción
 */

// Detectar la URL base automáticamente
function getApiBaseUrl() {
  // En producción (Render), usar VITE_API_URL si está definido
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // En desarrollo local, detectar desde el navegador
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname
    const protocol = window.location.protocol
    
    // Si es localhost o 127.0.0.1, usar localhost:5000
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:5000'
    }
    
    // Si es una IP o dominio, usar el mismo host con puerto 5000
    // Usar el mismo protocolo (http o https) que la página actual
    return `${protocol}//${hostname}:5000`
  }
  
  // Fallback por defecto
  return 'http://localhost:5000'
}

const API_BASE_URL = getApiBaseUrl()

// URL completa para endpoints de API
export const API_URL = `${API_BASE_URL}/api`

// URL para endpoints de sensor
export const SENSOR_API_URL = `${API_BASE_URL}/api/sensor`

// Exportar URL base para casos especiales
export default API_BASE_URL

