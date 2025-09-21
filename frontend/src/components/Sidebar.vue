<template>
  <aside class="w-20 bg-white shadow-md flex flex-col items-center py-8 min-h-screen">
    <nav class="flex flex-col gap-8">
      <router-link to="/" class="group flex flex-col items-center text-gray-400 hover:text-blue-500">
        <svg class="w-7 h-7 mb-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7m-9 2v8m4-8v8m5 0h-6a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2z" /></svg>
        <span class="text-xs">Inicio</span>
      </router-link>
      <router-link to="/admin" class="group flex flex-col items-center text-gray-400 hover:text-blue-500">
        <svg class="w-7 h-7 mb-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 1.343-3 3s1.343 3 3 3 3-1.343 3-3-1.343-3-3-3zm0 10c-4.418 0-8-1.79-8-4V7a2 2 0 012-2h12a2 2 0 012 2v7c0 2.21-3.582 4-8 4z" /></svg>
        <span class="text-xs">Admin</span>
      </router-link>
    </nav>
  </aside>
</template>
