<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-sm">
      <h2 class="text-2xl font-bold mb-6 text-center">Iniciar Sesión</h2>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block mb-1">Usuario</label>
          <input v-model="username" type="text" class="w-full border rounded px-3 py-2" required />
        </div>
        <div class="mb-6">
          <label class="block mb-1">Contraseña</label>
          <input v-model="password" type="password" class="w-full border rounded px-3 py-2" required />
        </div>
        <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">Entrar</button>
        <div v-if="error" class="text-red-600 mt-4 text-center">{{ error }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../services/authService'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

async function handleLogin() {
  error.value = ''
  try {
    const data = await login(username.value, password.value)
    if (data.rol === 'admin') {
      router.push('/admin')
    } else {
      router.push('/usuario')
    }
  } catch (e) {
    error.value = e.message
  }
}
</script>
