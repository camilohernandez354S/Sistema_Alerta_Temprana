# 🎛️ Integración Arduino - Frontend

## 📋 Resumen

Se ha implementado una integración completa entre el frontend Vue 3 y el Arduino (Mega + ESP8266) para controlar el buzzer y otros dispositivos remotamente.

## 🔧 Componentes Implementados

### 1. **Store de Pinia** (`src/stores/arduinoStore.js`)
- Manejo centralizado del estado de Arduino
- Funciones para enviar comandos
- Sistema de notificaciones integrado
- Historial de comandos

### 2. **Componente de Notificaciones** (`src/components/ToastNotifications.vue`)
- Sistema de toast para feedback visual
- Diferentes tipos: success, error, warning, info
- Auto-dismiss después de 5 segundos
- Animaciones suaves

### 3. **Panel de Control Arduino** (`src/components/ArduinoControlPanel.vue`)
- Interfaz completa para controlar el Arduino
- Botones para todos los comandos disponibles
- Indicador de estado de conexión
- Historial de comandos

### 4. **AlertsPanel Actualizado**
- Integración con el nuevo store
- Botón "Silenciar Buzzer" mejorado
- Indicador de conexión Arduino
- Feedback visual del último comando

## 🚀 Uso

### Comandos Disponibles

```javascript
import { useArduinoStore } from '../stores/arduinoStore'

const arduinoStore = useArduinoStore()

// Apagar buzzer
await arduinoStore.turnOffBuzzer()

// Activar buzzer
await arduinoStore.turnOnBuzzer('general', 1000)

// Obtener estado del dispositivo
await arduinoStore.getDeviceStatus()

// Reiniciar dispositivo
await arduinoStore.resetDevice()

// Comando genérico
await arduinoStore.sendCommand('BUZZER_OFF')
```

### Integración en Componentes

```vue
<template>
  <div>
    <button @click="apagarBuzzer" :disabled="arduinoStore.isLoading">
      🔇 Apagar Buzzer
    </button>
    
    <!-- Indicador de conexión -->
    <div v-if="arduinoStore.isConnected" class="text-green-500">
      ✅ Arduino conectado
    </div>
  </div>
</template>

<script setup>
import { useArduinoStore } from '../stores/arduinoStore'

const arduinoStore = useArduinoStore()

const apagarBuzzer = async () => {
  await arduinoStore.turnOffBuzzer()
}
</script>
```

## 📡 Flujo de Comunicación

1. **Frontend** → Envía comando JSON al endpoint `/api/mediciones/comando`
2. **Backend Flask** → Procesa comando y envía a Arduino via serial/HTTP
3. **ESP8266** → Recibe comando y lo envía al Mega via Serial
4. **Arduino Mega** → Ejecuta comando y responde
5. **Frontend** → Recibe confirmación y muestra notificación

## 🎨 Sistema de Notificaciones

### Tipos de Notificaciones
- ✅ **Success**: Comando ejecutado correctamente
- ❌ **Error**: Error al ejecutar comando
- ⚠️ **Warning**: Advertencias del sistema
- ℹ️ **Info**: Información general

### Personalización
```javascript
// Agregar notificación manual
arduinoStore.addNotification('success', 'Mensaje personalizado')

// Limpiar notificaciones
arduinoStore.clearNotifications()
```

## 🔌 Endpoint del Backend

### POST `/api/mediciones/comando`

**Request:**
```json
{
  "comando": "BUZZER_OFF",
  "parametros": {
    "alert_type": "general",
    "frequency": 1000
  }
}
```

**Response Success:**
```json
{
  "status": "success",
  "message": "Comando BUZZER_OFF enviado correctamente",
  "comando": "BUZZER_OFF",
  "resultado": { ... },
  "timestamp": "2025-01-21T10:30:00Z"
}
```

**Response Error:**
```json
{
  "status": "error",
  "message": "Error al ejecutar comando BUZZER_OFF",
  "comando": "BUZZER_OFF"
}
```

## 🎛️ Comandos Soportados

| Comando | Descripción | Parámetros |
|---------|-------------|------------|
| `BUZZER_OFF` | Apagar buzzer | Ninguno |
| `BUZZER_ON` | Activar buzzer | `alert_type`, `frequency` |
| `RESET` | Reiniciar dispositivo | Ninguno |
| `STATUS` | Obtener estado | Ninguno |

## 🔧 Configuración

### Variables de Entorno Backend
```bash
SERIAL_PORT=COM11
BAUD_RATE=9600
IOT_DEVICE_URL=http://arduino.local  # Opcional
```

### URL Base Frontend
```javascript
// En arduinoStore.js
const API_BASE_URL = 'http://localhost:5000'
```

## 📱 Componentes de Ejemplo

### Panel de Control Básico
```vue
<template>
  <ArduinoControlPanel />
</template>

<script setup>
import ArduinoControlPanel from '@/components/ArduinoControlPanel.vue'
</script>
```

### Integración en Dashboard
```vue
<template>
  <div class="dashboard">
    <!-- Otros componentes -->
    <ArduinoControlPanel v-if="esAdmin" />
    <AlertsPanel />
  </div>
</template>
```

## 🚨 Manejo de Errores

### Errores de Conexión
- Se muestra notificación de error
- Se actualiza estado de conexión
- Se mantiene historial de intentos

### Errores de Comando
- Feedback específico según el tipo de error
- Reintento automático (opcional)
- Logging detallado

## 🔄 Estado Reactivo

### Propiedades del Store
```javascript
// Estado
isLoading: boolean           // Si hay comando en proceso
lastCommand: object          // Último comando enviado
commandHistory: array        // Historial de comandos
connectionStatus: boolean    // Estado de conexión
notifications: array         // Notificaciones activas

// Getters
isConnected: computed        // Estado de conexión
hasRecentCommand: computed   // Si hay comando reciente
```

## 🎯 Próximas Mejoras

- [ ] Reintento automático de comandos fallidos
- [ ] Configuración de timeouts personalizables
- [ ] Logs detallados de comunicación
- [ ] Soporte para más comandos Arduino
- [ ] Dashboard de monitoreo en tiempo real
- [ ] Configuración de frecuencias personalizadas

## 🐛 Troubleshooting

### Problemas Comunes

1. **"Error de conexión"**
   - Verificar que el backend esté ejecutándose
   - Revisar configuración de puerto serial
   - Confirmar que Arduino esté conectado

2. **"Comando no soportado"**
   - Verificar que el comando esté en la lista soportada
   - Revisar formato del JSON enviado

3. **"Servicio no disponible"**
   - Verificar que DeviceControlService esté configurado
   - Revisar logs del backend

### Logs Útiles
```javascript
// Habilitar logs detallados
console.log('📤 Enviando comando:', payload)
console.log('📥 Respuesta:', result)
```
