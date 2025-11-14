/**
 * Servicio para manejar las alertas del sistema
 * Sigue el principio SRP (Single Responsibility Principle)
 */

import { SENSOR_API_URL } from '../config/api.js'

const API_BASE_URL = SENSOR_API_URL;

/**
 * Obtiene las alertas activas del sistema
 * @param {number} limit - Número máximo de alertas a obtener
 * @returns {Promise<Object>} Respuesta con las alertas
 */
export async function obtenerAlertas(limit = 10) {
  try {
    const response = await fetch(`${API_BASE_URL}/alertas?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error al obtener alertas:', error);
    throw new Error(`Error al obtener alertas: ${error.message}`);
  }
}

/**
 * Resuelve una alerta específica
 * @param {string} alertaId - ID de la alerta a resolver
 * @returns {Promise<Object>} Respuesta del servidor
 */
export async function resolverAlerta(alertaId) {
  try {
    const response = await fetch(`${API_BASE_URL}/alertas/${alertaId}/resolver`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error al resolver alerta:', error);
    throw new Error(`Error al resolver alerta: ${error.message}`);
  }
}

/**
 * Descarta una alerta específica
 * @param {string} alertaId - ID de la alerta a descartar
 * @returns {Promise<Object>} Respuesta del servidor
 */
export async function descartarAlerta(alertaId) {
  try {
    const response = await fetch(`${API_BASE_URL}/alertas/${alertaId}/descartar`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error al descartar alerta:', error);
    throw new Error(`Error al descartar alerta: ${error.message}`);
  }
}

/**
 * Obtiene estadísticas de alertas
 * @returns {Promise<Object>} Estadísticas de alertas
 */
export async function obtenerEstadisticasAlertas() {
  try {
    const response = await fetch(`${API_BASE_URL}/alertas/estadisticas`);
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error al obtener estadísticas de alertas:', error);
    throw new Error(`Error al obtener estadísticas de alertas: ${error.message}`);
  }
}

/**
 * Formatea una fecha para mostrar en la interfaz
 * @param {string} timestamp - Timestamp en formato ISO
 * @returns {string} Fecha formateada
 */
export function formatearFechaAlerta(timestamp) {
  try {
    const fecha = new Date(timestamp);
    return fecha.toLocaleString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  } catch (error) {
    console.error('Error al formatear fecha:', error);
    return timestamp;
  }
}

/**
 * Obtiene el color asociado a un tipo de alerta
 * @param {string} tipo - Tipo de alerta (sequía, inundación, normal)
 * @returns {Object} Objeto con clases CSS para el tipo de alerta
 */
export function obtenerEstilosAlerta(tipo) {
  const estilos = {
    'sequía': {
      cardClass: 'border-yellow-200 bg-yellow-50',
      textColor: 'text-yellow-700',
      icon: 'fas fa-sun text-yellow-500',
      badgeClass: 'bg-yellow-100 text-yellow-800'
    },
    'inundación': {
      cardClass: 'border-red-200 bg-red-50',
      textColor: 'text-red-700',
      icon: 'fas fa-water text-red-500',
      badgeClass: 'bg-red-100 text-red-800'
    },
    'normal': {
      cardClass: 'border-green-200 bg-green-50',
      textColor: 'text-green-700',
      icon: 'fas fa-check-circle text-green-500',
      badgeClass: 'bg-green-100 text-green-800'
    }
  };
  
  return estilos[tipo] || {
    cardClass: 'border-gray-200 bg-gray-50',
    textColor: 'text-gray-700',
    icon: 'fas fa-exclamation-triangle text-gray-500',
    badgeClass: 'bg-gray-100 text-gray-800'
  };
}

/**
 * Obtiene las etiquetas localizadas para los tipos de alerta
 * @param {string} tipo - Tipo de alerta
 * @returns {string} Etiqueta localizada
 */
export function obtenerEtiquetaTipoAlerta(tipo) {
  const etiquetas = {
    'sequía': 'Sequía',
    'inundación': 'Inundación',
    'normal': 'Normal'
  };
  
  return etiquetas[tipo] || tipo;
}

/**
 * Obtiene los estilos para los badges de estado
 * @param {string} estado - Estado de la alerta
 * @returns {string} Clases CSS para el badge
 */
export function obtenerEstilosEstado(estado) {
  const estilos = {
    'Activa': 'bg-red-100 text-red-800',
    'Resuelta': 'bg-green-100 text-green-800',
    'Descartada': 'bg-gray-100 text-gray-800'
  };
  
  return estilos[estado] || 'bg-gray-100 text-gray-800';
}
