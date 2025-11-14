<template>
  <AdminLayout page-title="Alertas" page-subtitle="Gestión y monitoreo de alertas del sistema">
    <div class="space-y-6">
      <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-6">
        <div class="flex items-center mb-4">
          <div class="w-10 h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center mr-3">
            <svg class="w-5 h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-[#005187]">Panel de Alertas</h2>
        </div>
        <div class="bg-[#c4dafa] rounded-lg p-4">
          <AlertsPanel />
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import AdminLayout from '../layouts/AdminLayout.vue'
import AlertsPanel from '../components/AlertsPanel.vue'
</script>

