<template>
  <AdminLayout page-title="Mapas" page-subtitle="Visualización geográfica de alertas y sensores">
    <div class="space-y-6">
      <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center">
            <div class="w-10 h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center mr-3">
              <svg class="w-5 h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
              </svg>
            </div>
            <h2 class="text-xl font-semibold text-[#005187]">Mapa de Alertas</h2>
          </div>
        </div>
        <div class="bg-[#c4dafa] rounded-lg p-8 min-h-[400px] flex items-center justify-center">
          <div class="text-center">
            <svg class="w-16 h-16 text-[#4d82bc] mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
            </svg>
            <p class="text-[#4d82bc] font-medium">Mapa interactivo próximamente</p>
            <p class="text-sm text-[#4d82bc] mt-2">Visualización geográfica de sensores y alertas</p>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import AdminLayout from '../layouts/AdminLayout.vue'
</script>

