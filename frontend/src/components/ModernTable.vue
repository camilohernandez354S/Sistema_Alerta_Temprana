<template>
  <div class="overflow-x-auto">
    <table class="w-full text-left rounded-xl overflow-hidden">
      <thead>
        <tr class="bg-gray-100 text-gray-500 text-xs uppercase">
          <th class="py-3 px-4">Usuario</th>
          <th class="py-3 px-4">Conversaciones</th>
          <th class="py-3 px-4">Duración</th>
          <th class="py-3 px-4">Canales</th>
          <th class="py-3 px-4">Enviadas</th>
          <th class="py-3 px-4">Recibidas</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in rows" :key="i" :class="i % 2 === 0 ? 'bg-gray-50' : 'bg-white'">
          <td class="py-3 px-4 flex items-center gap-3">
            <img :src="row.avatar" alt="avatar" class="w-8 h-8 rounded-full object-cover border border-gray-200" />
            <span class="font-medium text-gray-700">{{ row.usuario }}</span>
          </td>
          <td class="py-3 px-4">{{ row.conversaciones }}</td>
          <td class="py-3 px-4">{{ row.duracion }}</td>
          <td class="py-3 px-4">{{ row.canal }}</td>
          <td class="py-3 px-4">{{ row.enviadas }}</td>
          <td class="py-3 px-4">{{ row.recibidas }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
const props = defineProps({
  rows: {
    type: Array,
    default: () => []
  }
})
</script>
