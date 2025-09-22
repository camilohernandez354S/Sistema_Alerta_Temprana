<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-sm">
      <h2 class="text-2xl font-bold mb-6 text-center">Iniciar Sesión</h2>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block mb-1">Usuario</label>
          <input v-model="username" type="text" class="w-full border rounded px-3 py-2" :class="{'border-red-500': usernameError}" />
          <div v-if="usernameError" class="text-red-500 text-xs mt-1">El usuario es obligatorio</div>
        </div>
        <div class="mb-6">
          <label class="block mb-1">Contraseña</label>
          <input v-model="password" type="password" class="w-full border rounded px-3 py-2" :class="{'border-red-500': passwordError}" />
          <div v-if="passwordError" class="text-red-500 text-xs mt-1">La contraseña es obligatoria</div>
        </div>
        <button type="submit" :disabled="loading" :class="['w-full py-2 rounded', loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700', 'text-white']">
          <span v-if="loading">
            <svg class="animate-spin h-5 w-5 inline-block mr-2" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
            </svg>
            Entrando...
          </span>
          <span v-else>Entrar</span>
        </button>
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
const loading = ref(false)
const usernameError = ref(false)
const passwordError = ref(false)
const router = useRouter()

async function handleLogin() {
  error.value = ''
  usernameError.value = !username.value
  passwordError.value = !password.value
  if (usernameError.value || passwordError.value) {
    return
  }
  loading.value = true
  try {
    const data = await login(username.value, password.value)
    if (data.rol === 'admin') {
      router.push('/admin')
    } else {
      router.push('/usuario')
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
