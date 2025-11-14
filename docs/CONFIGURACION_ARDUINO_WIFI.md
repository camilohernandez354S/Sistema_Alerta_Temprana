# 🔌 Configuración Arduino WiFi desde .env

## 📋 Resumen

El Arduino WiFi (ESP8266/ESP32) se configura **automáticamente** desde tu archivo `.env`. Solo necesitas configurar las variables una vez y el sistema se encarga del resto.

---

## 🔧 Variables del .env que usa el Arduino

El Arduino WiFi lee estas variables del archivo `.env`:

### 1. Credenciales WiFi
```env
WIFI_SSID=nombre_de_tu_red_wifi
WIFI_PASSWORD=tu_contraseña_wifi
```

### 2. URL del Servidor Flask
```env
# Opción A: URL completa (recomendado)
FLASK_SERVER_URL=http://192.168.137.24:5000

# Opción B: IP y Puerto separados (fallback)
SERVER_IP=192.168.137.24
SERVER_PORT=5000
```

**Nota:** Si defines `FLASK_SERVER_URL`, se usa esa. Si no, se genera desde `SERVER_IP` y `SERVER_PORT`.

---

## 🚀 Proceso Automático

### Paso 1: Configurar .env

Edita tu archivo `.env` en la raíz del proyecto:

```env
# WiFi para Arduino
WIFI_SSID=MiRedWiFi
WIFI_PASSWORD=mi_contraseña_123

# Servidor (local o remoto)
FLASK_SERVER_URL=http://192.168.137.24:5000
# O para producción:
# FLASK_SERVER_URL=https://sat-backend.onrender.com
```

### Paso 2: Generar configuración WiFi

Ejecuta el script de verificación:

```powershell
.\scripts\verificar-config-arduino.ps1
```

Este script:
1. ✅ Lee tu `.env`
2. ✅ Valida que todas las variables estén configuradas
3. ✅ Genera `wifi_config.h` automáticamente
4. ✅ Muestra un resumen de la configuración

### Paso 3: Subir código al Arduino

1. Abre `backend/arduino/nivel_agua_wifi.ino` en Arduino IDE
2. El archivo `wifi_config.h` ya está generado
3. Selecciona tu placa (ESP8266 o ESP32)
4. Sube el código

---

## 🔄 Flujo de Configuración

```
.env (tu configuración)
    ↓
generar_config_wifi.py (lee .env)
    ↓
wifi_config.h (generado automáticamente)
    ↓
nivel_agua_wifi.ino (incluye wifi_config.h)
    ↓
Arduino (usa la configuración)
```

---

## 📝 Ejemplos de Configuración

### Ejemplo 1: Servidor Local
```env
WIFI_SSID=MiCasa_WiFi
WIFI_PASSWORD=password123
FLASK_SERVER_URL=http://192.168.137.24:5000
```

**Resultado:** Arduino se conecta a `MiCasa_WiFi` y envía datos a `http://192.168.137.24:5000`

### Ejemplo 2: Servidor Remoto (Producción)
```env
WIFI_SSID=MiCasa_WiFi
WIFI_PASSWORD=password123
FLASK_SERVER_URL=https://sat-backend.onrender.com
```

**Resultado:** Arduino se conecta a `MiCasa_WiFi` y envía datos a `https://sat-backend.onrender.com` (HTTPS automático)

### Ejemplo 3: Sin FLASK_SERVER_URL (usa SERVER_IP)
```env
WIFI_SSID=MiCasa_WiFi
WIFI_PASSWORD=password123
SERVER_IP=192.168.137.24
SERVER_PORT=5000
```

**Resultado:** Se genera automáticamente `http://192.168.137.24:5000`

---

## ✅ Verificación

### Ver configuración actual

```powershell
python backend\arduino\network_config.py
```

O usa el script de verificación:

```powershell
.\scripts\verificar-config-arduino.ps1
```

### Verificar wifi_config.h generado

Abre `backend/arduino/wifi_config.h` y verifica:

```cpp
#define WIFI_SSID "MiCasa_WiFi"
#define WIFI_PASSWORD "password123"
#define SERVER_HOST "sat-backend.onrender.com"
#define SERVER_PORT 443
#define USE_HTTPS 1
```

---

## 🔧 Cambiar Configuración

Si necesitas cambiar la configuración:

1. **Edita `.env`** con los nuevos valores
2. **Regenera `wifi_config.h`:**
   ```powershell
   python backend\arduino\generar_config_wifi.py
   ```
3. **Vuelve a subir el código** al Arduino

---

## ⚠️ Importante

- ✅ **NO edites `wifi_config.h` manualmente** - Se sobrescribirá
- ✅ **Edita siempre `.env`** - Es la fuente de verdad
- ✅ **Regenera después de cambiar `.env`** - Ejecuta el script
- ✅ **Verifica antes de subir** - Usa el script de verificación

---

## 🐛 Solución de Problemas

### Error: "WIFI_SSID no está configurado"
**Solución:** Agrega `WIFI_SSID=tu_red` al `.env`

### Error: "No se encontró archivo .env"
**Solución:** Copia `config/example.env` a `.env` y configúralo

### Arduino no se conecta a WiFi
**Solución:**
1. Verifica que `WIFI_SSID` y `WIFI_PASSWORD` sean correctos
2. Regenera `wifi_config.h`
3. Vuelve a subir el código

### Arduino no envía datos al servidor
**Solución:**
1. Verifica que `FLASK_SERVER_URL` sea correcto
2. Verifica que el servidor esté accesible
3. Revisa el monitor serial del Arduino para ver errores

---

## 📚 Archivos Relacionados

- `backend/arduino/generar_config_wifi.py` - Script generador
- `backend/arduino/network_config.py` - Módulo de configuración
- `backend/arduino/nivel_agua_wifi.ino` - Código Arduino
- `backend/arduino/wifi_config.h` - Configuración generada (no editar)
- `scripts/verificar-config-arduino.ps1` - Script de verificación

---

## 🎯 Resumen

**Todo está centralizado en `.env`:**
- ✅ WiFi SSID → `WIFI_SSID`
- ✅ WiFi Password → `WIFI_PASSWORD`
- ✅ Servidor → `FLASK_SERVER_URL` (o `SERVER_IP` + `SERVER_PORT`)

**Un solo comando para configurar:**
```powershell
.\scripts\verificar-config-arduino.ps1
```

¡Así de simple! 🚀

