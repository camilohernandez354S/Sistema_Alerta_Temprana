# 🚨 Sistema de Alertas - Documentación Completa

## Resumen

Sistema integral de alertas en tiempo real para el Sistema de Alerta Temprana, que permite evidenciar estados de medición de sensores de nivel de agua y controlar manualmente las alarmas físicas (buzzer).

## 📋 Características Implementadas

### ✅ Estados de Alerta
- **Inundación**: Nivel ≤ 15cm (configurable via `UMBRAL_INUNDACION`)
- **Sequía**: Nivel ≥ 40cm (configurable via `UMBRAL_SEQUIA`)  
- **Normal**: Nivel entre 15cm y 40cm (no genera alerta)

### ✅ Visualización en Panel de Admin
- Estado actual del sistema en tiempo real
- Lista de alertas activas con diferenciación visual
- Historial completo de alertas
- Indicadores de colores: 🔴 Inundación, 🟡 Sequía, 🟢 Normal
- Actualización automática cada 30 segundos

### ✅ Control Manual de Buzzer
- Botón para desactivar alerta activa (solo admins)
- Botón para silenciar buzzer general
- Control remoto del buzzer del Arduino via serial
- Configuración de tonos según tipo de alerta

### ✅ Persistencia y Backend
- Almacenamiento en MongoDB con esquema completo
- Endpoints RESTful protegidos con JWT
- Procesamiento automático de nuevas mediciones
- Integración con sistema de control de dispositivos IoT

### ✅ Seguridad y Roles
- Solo rol `admin` puede desactivar alertas
- Usuarios normales pueden ver alertas (solo lectura)
- Autenticación JWT en todos los endpoints
- Logging completo de acciones administrativas

## 🏗️ Arquitectura del Sistema

```
Arduino Sensor → Backend Flask → MongoDB
     ↓               ↓              ↓
Control Buzzer ← Alerts Service → Frontend Vue.js
```

## 📊 Esquema de Base de Datos

### Colección: `alertas`

```javascript
{
  _id: ObjectId,
  tipo_alerta: "inundacion" | "sequia" | "normal",
  nivel_agua: Number,          // Nivel en cm
  alerta_activa: Boolean,      // true si está activa
  timestamp: Date,             // Fecha de creación
  fecha_desactivacion: Date,   // Fecha de desactivación (null si activa)
  desactivada_por: String,     // Usuario que desactivó o "system_auto"
  motivo_desactivacion: String, // Motivo de desactivación
  buzzer_activo: Boolean,      // true si buzzer está sonando
  creada_por: String,          // Usuario/sistema que creó la alerta
  descripcion: String          // Descripción legible de la alerta
}
```

## 🔗 Endpoints de la API

### Base URL: `http://localhost:5000/api/v1`

### 1. Obtener Alertas
```http
GET /alertas?activas=true&limite=50
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "alertas": [...],
  "total": 5,
  "filtros": {
    "solo_activas": true,
    "limite": 50
  },
  "timestamp": "2025-01-21T10:30:00.000Z"
}
```

### 2. Estado del Sistema
```http
GET /alertas/estado
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "nivel_actual": 25.5,
  "estado_actual": "normal",
  "alertas_activas": 0,
  "buzzer_activo": false,
  "ultima_actualizacion": "2025-01-21T10:30:00.000Z",
  "umbrales": {
    "inundacion": 15.0,
    "sequia": 40.0
  }
}
```

### 3. Desactivar Alerta (Solo Admin)
```http
PATCH /alertas/{alerta_id}/desactivar
Authorization: Bearer <token>
Content-Type: application/json

{
  "motivo": "desactivacion_manual_admin_panel"
}
```

### 4. Desactivar Buzzer General (Solo Admin)
```http
POST /alertas/buzzer/desactivar
Authorization: Bearer <token>
```

### 5. Configuración de Umbrales
```http
GET /alertas/configuracion
Authorization: Bearer <token>
```

### 6. Estadísticas de Alertas
```http
GET /alertas/estadisticas
Authorization: Bearer <token>
```

### 7. Pruebas de Dispositivo (Solo Admin)
```http
POST /dispositivos/test
Authorization: Bearer <token>
Content-Type: application/json

{
  "test_type": "buzzer_on" | "buzzer_off" | "connection" | "status"
}
```

### 8. Health Check
```http
GET /alertas/health
```

## 🖥️ Componente Frontend

### AlertsPanel.vue

**Características:**
- Visualización en tiempo real del estado del sistema
- Lista filtrable de alertas (activas/todas, por tipo)
- Botones de acción para administradores
- Actualización automática cada 30 segundos
- Interfaz responsiva con Tailwind CSS

**Uso:**
```vue
<template>
  <AlertsPanel />
</template>

<script setup>
import AlertsPanel from '@/components/AlertsPanel.vue'
</script>
```

## 🔧 Control de Dispositivos IoT

### Servicio DeviceControlService

**Funcionalidades:**
- Comunicación serial con Arduino
- Control remoto del buzzer
- Configuración de tonos por tipo de alerta
- Fallback a simulación si no hay conexión

**Comandos soportados:**
- `BUZZER_ON` - Activar buzzer con frecuencia
- `BUZZER_OFF` - Desactivar buzzer
- `STATUS` - Obtener estado del dispositivo
- `RESET` - Reiniciar configuración

## 📱 Arduino - Código Actualizado

### Nuevas características:
- Procesamiento de comandos seriales JSON
- Control remoto del buzzer
- Respuestas estructuradas
- Separación de control LED/buzzer

### Comandos JSON soportados:
```json
{"command": "BUZZER_ON", "frequency": 1500, "timestamp": 1642781234}
{"command": "BUZZER_OFF", "timestamp": 1642781234}
{"command": "STATUS", "timestamp": 1642781234}
```

## ⚙️ Configuración

### Variables de Entorno

```bash
# Umbrales de alerta
UMBRAL_INUNDACION=15.0
UMBRAL_SEQUIA=40.0

# Comunicación con Arduino
SERIAL_PORT=COM11
BAUD_RATE=9600
IOT_DEVICE_URL=http://arduino.local  # Opcional para HTTP

# MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=sistema_alerta

# Logging
LOG_LEVEL=INFO
```

## 🚀 Instalación y Ejecución

### 1. Backend
```bash
cd backend/backend-flask
pip install -r requirements.txt
python run.py
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Arduino
```bash
# Subir nivel_agua.ino al Arduino
# Configurar puerto serial en .env
cd backend/arduino
pip install -r requirements.txt
python leer_serial.py
```

## 🧪 Pruebas

### Probar Conexión con Dispositivo
```bash
curl -X POST http://localhost:5000/api/v1/dispositivos/test \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"test_type": "connection"}'
```

### Simular Alerta de Inundación
```bash
curl -X POST http://localhost:5000/api/mediciones \
  -H "Content-Type: application/json" \
  -d '{"distancia": 10.0}'
```

### Desactivar Alerta
```bash
curl -X PATCH http://localhost:5000/api/v1/alertas/{id}/desactivar \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"motivo": "prueba_manual"}'
```

## 📊 Logging

### Logs de Alertas
```
2025-01-21 10:30:00 - alerts_service - INFO - NUEVA_ALERTA - tipo=inundacion, nivel=12.5cm, id=60f7b1234567890123456789, user=arduino_sensor
2025-01-21 10:35:00 - alerts_service - INFO - ALERTA_DESACTIVADA_MANUAL - id=60f7b1234567890123456789, tipo=inundacion, user=admin, motivo=desactivacion_manual_admin_panel
```

### Logs de Dispositivos
```
2025-01-21 10:30:00 - device_control - INFO - BUZZER_ACTIVADO - tipo=inundacion, frecuencia=1500Hz
2025-01-21 10:35:00 - device_control - INFO - BUZZER_DESACTIVADO
```

## 🔍 Monitoreo y Observabilidad

### Health Check
```bash
curl http://localhost:5000/api/v1/alertas/health
```

### Estadísticas
- Total de alertas generadas
- Alertas activas actuales
- Alertas en las últimas 24 horas
- Distribución por tipo de alerta

## 🛡️ Seguridad

### Autenticación
- JWT tokens con expiración de 2 horas
- Roles diferenciados: `admin` y `usuario`
- Middleware de autenticación en todos los endpoints protegidos

### Autorización
- Solo administradores pueden desactivar alertas
- Solo administradores pueden controlar buzzer
- Solo administradores pueden ejecutar pruebas de dispositivos

### Validación
- Validación de IDs de alerta (formato ObjectId)
- Sanitización de parámetros de entrada
- Manejo seguro de errores sin exposición de información sensible

## 🔄 Flujo de Datos Completo

1. **Arduino** mide nivel de agua cada 5 segundos
2. **leer_serial.py** recibe datos y los envía al backend
3. **Backend** procesa medición y evalúa si genera alerta
4. Si hay alerta, se almacena en **MongoDB** y se activa **buzzer**
5. **Frontend** muestra alertas en tiempo real
6. **Admin** puede desactivar alertas desde el panel
7. **Backend** envía comando al **Arduino** para desactivar buzzer
8. Se registra la acción en **logs** para auditoría

## 🎯 Casos de Uso

### Caso 1: Alerta de Inundación
1. Sensor detecta nivel ≤ 15cm
2. Sistema genera alerta automáticamente
3. Buzzer suena con tono agudo (1500Hz)
4. LED rojo se enciende
5. Panel admin muestra alerta activa
6. Admin puede silenciar buzzer desde panel

### Caso 2: Alerta de Sequía
1. Sensor detecta nivel ≥ 40cm
2. Sistema genera alerta automáticamente
3. Buzzer suena con tono grave (400Hz)
4. LED verde se enciende
5. Panel admin muestra alerta activa
6. Admin puede desactivar alerta completa

### Caso 3: Vuelta a Normalidad
1. Sensor detecta nivel entre 15-40cm
2. Sistema desactiva alertas automáticamente
3. Buzzer se silencia
4. LED amarillo se enciende
5. Panel muestra estado normal

## 🔧 Mantenimiento

### Logs a Monitorear
- Errores de conexión con Arduino
- Fallos en base de datos
- Alertas no procesadas
- Comandos de buzzer fallidos

### Backups
- Respaldar colección `alertas` de MongoDB
- Respaldar configuración de umbrales
- Mantener logs por al menos 30 días

### Actualizaciones
- Actualizar umbrales según condiciones locales
- Calibrar sensor periódicamente
- Probar sistema de alertas semanalmente

## 📞 Soporte

Para problemas o preguntas sobre el sistema de alertas:

1. Verificar logs de aplicación
2. Probar conexión con dispositivo IoT
3. Validar configuración de umbrales
4. Revisar estado de MongoDB
5. Contactar al equipo de desarrollo

---

**Versión del Sistema:** 1.0  
**Última Actualización:** Enero 2025  
**Autor:** Sistema de Alerta Temprana Team
