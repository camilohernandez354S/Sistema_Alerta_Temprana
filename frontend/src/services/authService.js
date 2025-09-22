// authService.js
// Servicio de autenticación para el frontend

const API_BASE_URL = 'http://localhost:5000'

// Función para realizar login
export async function login(username, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        password
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Error en el login')
    }

    const data = await response.json()
    
    // Guardar token y rol en localStorage
    localStorage.setItem('token', data.token)
    localStorage.setItem('rol', data.rol)
    localStorage.setItem('username', username)
    
    return data
  } catch (error) {
    console.error('Error en login:', error)
    throw new Error(error.message)
  }
}

// Función para obtener el token
export function getToken() {
  return localStorage.getItem('token')
}

// Función para obtener el rol del usuario
export function getRol() {
  return localStorage.getItem('rol')
}

// Función para obtener el username
export function getUsername() {
  return localStorage.getItem('username')
}

// Función para verificar si el usuario está autenticado
export function isAuthenticated() {
  const token = getToken()
  return !!token
}

// Función para cerrar sesión
export function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('rol')
  localStorage.removeItem('username')
}

// Función para verificar el token con el servidor
export async function verifyToken() {
  const token = getToken()
  if (!token) {
    return false
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/verify-token`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      }
    })

    if (response.ok) {
      const data = await response.json()
      return data.valid
    } else {
      // Token inválido, limpiar localStorage
      logout()
      return false
    }
  } catch (error) {
    console.error('Error verificando token:', error)
    return false
  }
}

// Función para hacer peticiones autenticadas
export async function authenticatedFetch(url, options = {}) {
  const token = getToken()
  
  if (!token) {
    throw new Error('No hay token de autenticación')
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers
  }

  const response = await fetch(url, {
    ...options,
    headers
  })

  // Si el token es inválido, cerrar sesión
  if (response.status === 401) {
    logout()
    throw new Error('Sesión expirada')
  }

  return response
}
