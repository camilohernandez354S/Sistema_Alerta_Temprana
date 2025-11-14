<template>
  <AdminLayout page-title="Mediciones" page-subtitle="Historial completo de mediciones del sistema">
    <MedicionesTable />
  </AdminLayout>
</template>

<script setup>
import AdminLayout from '../layouts/AdminLayout.vue'
import MedicionesTable from '../components/MedicionesTable.vue'
</script>

