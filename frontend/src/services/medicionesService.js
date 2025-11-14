import { API_URL } from '../config/api.js'

const MEDICIONES_API_URL = `${API_URL}/mediciones`;

export async function obtenerMediciones() {
  const response = await fetch(MEDICIONES_API_URL);
  if (!response.ok) {
    throw new Error('Error al obtener las mediciones');
  }
  return await response.json();
}
