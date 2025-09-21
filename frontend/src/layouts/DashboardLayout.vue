<template>
  <div class="min-h-screen bg-gray-50 font-sans">
    <HeaderBar />
    <div class="flex">
      <Sidebar />
      <main class="flex-1 p-8">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import HeaderBar from '../components/HeaderBar.vue'
import Sidebar from '../components/Sidebar.vue'
</script>
