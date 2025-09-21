<template>
  <div>
    <h1>Dashboard de Mediciones</h1>
    <ul>
      <li v-for="medicion in mediciones" :key="medicion._id">
        {{ medicion.fecha }} - {{ medicion.distancia }} cm
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { obtenerMediciones } from '../services/medicionesService'

const mediciones = ref([])

onMounted(async () => {
  try {
    mediciones.value = await obtenerMediciones()
  } catch (error) {
    alert(error.message)
  }
})
</script>
