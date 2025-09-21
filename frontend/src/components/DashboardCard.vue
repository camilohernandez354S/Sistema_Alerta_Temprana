<template>
  <div class="max-w-5xl mx-auto bg-white rounded-3xl shadow-xl p-8 mt-10">
    <div class="flex flex-col md:flex-row gap-8">
      <div class="flex-1 flex flex-col items-center justify-center">
        <h2 class="text-lg font-semibold text-gray-700 mb-4">Canales</h2>
        <!-- Aquí va el gráfico radial/radar/dona -->
        <slot name="grafico-izq" />
      </div>
      <div class="flex-1 flex flex-col items-center justify-center">
        <h2 class="text-lg font-semibold text-gray-700 mb-4">Mensajes</h2>
        <!-- Aquí va el gráfico de barras -->
        <slot name="grafico-der" />
      </div>
    </div>
    <div class="mt-8">
      <slot name="tabla" />
    </div>
  </div>
</template>
