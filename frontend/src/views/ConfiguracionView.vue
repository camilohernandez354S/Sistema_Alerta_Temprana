<template>
  <AdminLayout page-title="Configuración" page-subtitle="Ajustes y parámetros del sistema">
    <div class="space-y-6">
      <!-- Panel de Control de Dispositivos -->
      <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-6">
        <div class="flex items-center mb-4">
          <div class="w-10 h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center mr-3">
            <svg class="w-5 h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-[#005187]">Control de Dispositivos</h2>
        </div>
        <div class="space-y-3">
          <div class="flex items-center justify-between p-3 bg-[#c4dafa] rounded-lg border border-[#84b6f4]">
            <span class="text-sm font-medium text-[#005187]">Estado del Sistema</span>
            <span class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">Activo</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-[#c4dafa] rounded-lg border border-[#84b6f4]">
            <span class="text-sm font-medium text-[#005187]">Conexión Arduino</span>
            <span class="px-3 py-1 bg-[#84b6f4] text-[#005187] rounded-full text-xs font-medium">Conectado</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-[#c4dafa] rounded-lg border border-[#84b6f4]">
            <span class="text-sm font-medium text-[#005187]">Base de Datos</span>
            <span class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">Online</span>
          </div>
        </div>
      </div>

      <!-- Configuración General -->
      <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-6">
        <h2 class="text-xl font-semibold text-[#005187] mb-4">Configuración General</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-[#005187] mb-2">Intervalo de Lectura (segundos)</label>
            <input type="number" value="5" class="w-full px-4 py-2 border border-[#c4dafa] rounded-lg bg-[#fcffff] text-[#005187] focus:outline-none focus:border-[#005187]" />
          </div>
          <div>
            <label class="block text-sm font-medium text-[#005187] mb-2">Umbral de Alerta (cm)</label>
            <input type="number" value="400" class="w-full px-4 py-2 border border-[#c4dafa] rounded-lg bg-[#fcffff] text-[#005187] focus:outline-none focus:border-[#005187]" />
          </div>
          <button class="w-full px-4 py-2 bg-[#005187] text-white rounded-lg hover:bg-[#4d82bc] transition-colors duration-150 font-medium">
            Guardar Configuración
          </button>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import AdminLayout from '../layouts/AdminLayout.vue'
</script>

