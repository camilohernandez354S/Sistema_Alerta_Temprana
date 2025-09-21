const API_URL = 'http://localhost:5000/api';

export async function login(username, password) {
  const response = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Error de autenticación');
  }
  localStorage.setItem('token', data.token);
  localStorage.setItem('rol', data.rol);
  return data;
}

export function getToken() {
  return localStorage.getItem('token');
}

export function getRol() {
  return localStorage.getItem('rol');
}

export function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('rol');
}
