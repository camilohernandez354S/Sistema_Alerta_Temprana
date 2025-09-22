<template>
  <div class="login-dark-bg">
    <div class="login-card">
      <form @submit.prevent="handleLogin" autocomplete="off">
        <h2 class="login-title">Iniciar Sesión</h2>
        <div class="avatar-dark">
          <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" alt="avatar" />
        </div>
        <!-- USUARIO -->
        <div class="input-group">
          <input
            class="input-dark"
            type="text"
            name="usuario"
            placeholder=" "
            v-model="username"
            :class="{'has-val': username}"
            autocomplete="username"
            required
          />
          <label class="input-label">Usuario</label>
          <span class="input-underline"></span>
          <div v-if="usernameError" class="input-error">El usuario es obligatorio</div>
        </div>
        <!-- CONTRASEÑA -->
        <div class="input-group">
          <input
            class="input-dark"
            type="password"
            name="password"
            placeholder=" "
            v-model="password"
            :class="{'has-val': password}"
            autocomplete="current-password"
            required
          />
          <label class="input-label">Contraseña</label>
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
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@600&display=swap');
.login-dark-bg {
  min-height: 100vh;
  width: 100vw;
  background: #0a0a0f;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Baloo 2', cursive, Arial, sans-serif;
  transition: background 0.7s;
}
.login-card {
  background: #181824;
  border-radius: 24px;
  box-shadow: 0 8px 40px 0 #000a  ;
  padding: 3rem 2.5rem 2.5rem 2.5rem;
  min-width: 350px;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: fadeInUp 1s cubic-bezier(.23,1.01,.32,1) both;
}
@keyframes fadeInUp {
  0% { opacity: 0; transform: translateY(40px); }
  100% { opacity: 1; transform: translateY(0); }
}
.login-title {
  color: #fff;
  font-size: 2.3rem;
  font-weight: 700;
  margin-bottom: 1.2rem;
  letter-spacing: 1px;
  text-align: center;
}
.avatar-dark {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 1.5rem;
}
.avatar-dark img {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  border: 3px solid #00c3ff;
  box-shadow: 0 0 16px #00c3ff88;
  background: #222;
  animation: avatarPop 1.2s cubic-bezier(.23,1.01,.32,1);
}
@keyframes avatarPop {
  0% { transform: scale(0.7); opacity: 0; }
  80% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); }
}
.input-group {
  position: relative;
  margin-bottom: 2.2rem;
  width: 100%;
}
.input-dark {
  width: 100%;
  padding: 1.1rem 1rem 0.6rem 1rem;
  background: #232336;
  border: none;
  border-radius: 10px 10px 0 0;
  color: #fff;
  font-size: 1.1rem;
  outline: none;
  transition: background 0.4s, box-shadow 0.4s;
  box-shadow: 0 2px 8px 0 #00c3ff22;
  z-index: 2;
}
.input-dark:focus {
  background: #232346;
  box-shadow: 0 0 0 2px #00c3ff, 0 2px 8px 0 #00c3ff44;
}
.input-label {
  position: absolute;
  left: 1rem;
  top: 1.1rem;
  color: #7fd7ff;
  font-size: 1.1rem;
  pointer-events: none;
  transition: 0.3s cubic-bezier(.23,1.01,.32,1);
  z-index: 3;
}
.input-dark:focus + .input-label,
.has-val.input-dark + .input-label {
  top: -1.1rem;
  left: 0.5rem;
  font-size: 0.95rem;
  color: #00c3ff;
  letter-spacing: 1px;
}
.input-underline {
  position: absolute;
  left: 0;
  bottom: 0.2rem;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #00c3ff 0%, #0050ff 100%);
  border-radius: 2px;
  transform: scaleX(0);
  transition: transform 0.4s cubic-bezier(.23,1.01,.32,1);
  z-index: 1;
}
.input-dark:focus ~ .input-underline,
.has-val.input-dark ~ .input-underline {
  transform: scaleX(1);
}
.input-error {
  color: #ff4b6e;
  font-size: 0.95rem;
  margin-top: 0.3rem;
  text-shadow: 0 1px 2px #000a;
}
.login-btn {
  width: 100%;
  padding: 0.9rem 0;
  background: linear-gradient(90deg, #00c3ff 0%, #0050ff 100%);
  color: #fff;
  font-size: 1.2rem;
  font-family: 'Baloo 2', cursive, Arial, sans-serif;
  border: none;
  border-radius: 12px;
  margin-top: 0.5rem;
  font-weight: 700;
  letter-spacing: 2px;
  box-shadow: 0 2px 16px 0 #00c3ff44;
  transition: background 0.3s, transform 0.2s, box-shadow 0.3s;
  position: relative;
  overflow: hidden;
  z-index: 2;
}
.login-btn:active {
  transform: scale(0.97);
}
.login-btn:before {
  content: '';
  position: absolute;
  left: -75%;
  top: 0;
  width: 50%;
  height: 100%;
  background: rgba(255,255,255,0.13);
  transform: skewX(-20deg);
  transition: left 0.5s cubic-bezier(.23,1.01,.32,1);
  z-index: 1;
}
.login-btn:hover:before {
  left: 120%;
}
.login-btn:disabled {
  background: #222a;
  color: #888;
  cursor: not-allowed;
  box-shadow: none;
}
.login-error {
  color: #ff4b6e;
  margin-top: 1.2rem;
  text-align: center;
  font-size: 1.1rem;
  text-shadow: 0 1px 2px #000a;
}
</style>
