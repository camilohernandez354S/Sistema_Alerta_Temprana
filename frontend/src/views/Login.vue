<template>
  <div class="login-dark-bg">
    <div class="login-card">
      <form @submit.prevent="handleLogin" autocomplete="off">
        <div class="system-header">
          <h1 class="system-title">Sistema de Alerta Temprana</h1>
          <p class="system-subtitle">Monitoreo de Nivel de Agua</p>
        </div>
        <h2 class="login-title">Iniciar Sesión</h2>
        <div class="avatar-dark">
          <div class="system-icon">
            <div class="icon-wrapper">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="rotating-logo">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="#005187"/>
                <path d="M12 18L13.5 20.5L16 19L13.5 21.5L12 24L10.5 21.5L8 19L10.5 20.5L12 18Z" fill="#4d82bc"/>
                <circle cx="12" cy="12" r="3" fill="#84b6f4" opacity="0.4"/>
              </svg>
            </div>
          </div>
        </div>
        <!-- USUARIO -->
        <div class="input-group">
          <input
            id="username"
            class="input-dark"
            type="text"
            name="usuario"
            placeholder=" "
            v-model="username"
            :class="{'has-val': username}"
            autocomplete="username"
            required
          />
          <label for="username" class="input-label">Usuario</label>
          <span class="input-underline"></span>
          <div v-if="usernameError" class="input-error">El usuario es obligatorio</div>
        </div>
        <!-- CONTRASEÑA -->
        <div class="input-group">
          <input
            id="password"
            class="input-dark"
            type="password"
            name="password"
            placeholder=" "
            v-model="password"
            :class="{'has-val': password}"
            autocomplete="current-password"
            required
          />
          <label for="password" class="input-label">Contraseña</label>
          <span class="input-underline"></span>
          <div v-if="passwordError" class="input-error">La contraseña es obligatoria</div>
        </div>
        <!-- BOTÓN -->
        <button type="submit" name="btnEntrar" class="login-btn" :disabled="loading">
          <span v-if="loading">
            <svg class="animate-spin h-5 w-5 inline-block mr-2" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
            </svg>
            Entrando...
          </span>
          <span v-else>ENTRAR</span>
        </button>
        <div v-if="error" class="login-error">{{ error }}</div>
        <div class="system-footer">
          <p class="system-info">🔍 Monitoreo en tiempo real • ⚡ Alertas automáticas • 📊 Dashboard inteligente</p>
        </div>
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

<style scoped>
.login-dark-bg {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #aaaaaa 0%, #b8b8b8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: system-ui, -apple-system, sans-serif;
  position: relative;
  overflow: hidden;
  padding: 1rem;
  box-sizing: border-box;
}

.login-dark-bg::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(0, 81, 135, 0.05) 0%, transparent 70%);
  animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.login-card {
  background: #fcffff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 81, 135, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 1.5rem 1.75rem;
  width: 100%;
  max-width: 400px;
  max-height: 95vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid #c4dafa;
  animation: fadeInUp 0.6s ease-out;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
  margin: 0 auto;
  overflow-y: auto;
}

@media (min-width: 640px) {
  .login-card {
    padding: 2rem 2.5rem;
    border-radius: 20px;
  }
}

@keyframes fadeInUp {
  0% { 
    opacity: 0; 
    transform: translateY(30px) scale(0.95); 
  }
  100% { 
    opacity: 1; 
    transform: translateY(0) scale(1); 
  }
}

.system-header {
  text-align: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #c4dafa;
  width: 100%;
  position: relative;
}

.system-header::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #005187, transparent);
}

.system-title {
  color: #005187;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
  letter-spacing: 0.3px;
  background: linear-gradient(135deg, #005187 0%, #4d82bc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.system-subtitle {
  color: #4d82bc;
  font-size: 0.875rem;
  margin: 0;
  font-weight: 400;
  letter-spacing: 0.2px;
}

.login-title {
  color: #005187;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  text-align: center;
  letter-spacing: 0.3px;
}

.avatar-dark {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 1.25rem;
}

.system-icon {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  border: 2px solid #c4dafa;
  background: linear-gradient(135deg, #fcffff 0%, #e8f2ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(0, 81, 135, 0.15), 
              0 0 0 1px rgba(0, 81, 135, 0.05);
  position: relative;
  transition: all 0.3s ease;
}

.system-icon:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 81, 135, 0.2), 
              0 0 0 1px rgba(0, 81, 135, 0.1);
}

.icon-wrapper {
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rotating-logo {
  width: 35px;
  height: 35px;
  animation: rotate 8s linear infinite;
  transform-origin: center;
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.input-group {
  position: relative;
  margin-bottom: 1.25rem;
  width: 100%;
}

.input-dark {
  width: 100%;
  padding: 0.875rem 0.875rem 0.625rem 0.875rem;
  background: #fcffff;
  border: 2px solid #c4dafa;
  border-radius: 10px;
  color: #005187;
  font-size: 0.9375rem;
  outline: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
}

.input-dark::placeholder {
  color: transparent;
}

.input-dark:focus {
  border-color: #005187;
  box-shadow: 0 0 0 4px rgba(0, 81, 135, 0.1),
              0 2px 8px rgba(0, 81, 135, 0.1);
  transform: translateY(-1px);
}

.input-label {
  position: absolute;
  left: 0.875rem;
  top: 0.875rem;
  color: #4d82bc;
  font-size: 0.9375rem;
  pointer-events: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 3;
  background: transparent;
}

.input-dark:focus + .input-label,
.has-val.input-dark + .input-label {
  top: -0.625rem;
  left: 0.75rem;
  font-size: 0.8125rem;
  color: #005187;
  background: #fcffff;
  padding: 0 0.375rem;
  font-weight: 500;
}

.input-underline {
  display: none;
}

.input-error {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  padding-left: 0.25rem;
  animation: shake 0.3s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

.login-btn {
  width: 100%;
  padding: 0.875rem 0;
  background: linear-gradient(135deg, #005187 0%, #4d82bc 100%);
  color: #fff;
  font-size: 1rem;
  border: none;
  border-radius: 10px;
  margin-top: 0.5rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 81, 135, 0.2);
}

.login-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.login-btn:hover::before {
  left: 100%;
}

.login-btn:hover {
  background: linear-gradient(135deg, #4d82bc 0%, #005187 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 81, 135, 0.3);
}

.login-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 81, 135, 0.2);
}

.login-btn:disabled {
  background: #c4dafa;
  color: #84b6f4;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.login-btn:disabled::before {
  display: none;
}

.login-error {
  color: #dc2626;
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
  padding: 0.75rem 1rem;
  background: rgba(220, 38, 38, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(220, 38, 38, 0.2);
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.system-footer {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #c4dafa;
  text-align: center;
  width: 100%;
}

.system-info {
  color: #4d82bc;
  font-size: 0.75rem;
  margin: 0;
  line-height: 1.5;
  letter-spacing: 0.2px;
}

.system-info::before,
.system-info::after {
  content: '•';
  margin: 0 0.5rem;
  color: #84b6f4;
}
</style>
