const API_URL = 'http://localhost:5000/api/mediciones';

export async function obtenerMediciones() {
  const response = await fetch(API_URL);
  if (!response.ok) {
    throw new Error('Error al obtener las mediciones');
  }
  return await response.json();
}
