<template>
  <div class="bg-white rounded-xl shadow p-6 flex flex-col items-center min-w-[180px]">
    <div :class="['text-3xl font-bold mb-2', accentClass]">{{ value }}</div>
    <div class="text-gray-500 text-sm">{{ title }}</div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: String,
  value: [String, Number],
  accent: {
    type: String,
    default: 'blue'
  }
})
const accentClass = `text-${props.accent}-500`
</script>
