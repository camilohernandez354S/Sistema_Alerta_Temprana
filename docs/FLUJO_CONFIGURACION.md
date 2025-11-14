# 🔄 Flujo de Configuración desde .env

## 📋 Resumen

Todo el sistema lee la configuración desde un **único archivo `.env`** en la raíz del proyecto. Este archivo centraliza:
- **IP del servidor** (`SERVER_IP`)
- **Nombre de la red WiFi** (`WIFI_SSID`)
- **Contraseña WiFi** (`WIFI_PASSWORD`)
- **URL del servidor Flask** (`FLASK_SERVER_URL`)

---

## 📁 Archivo .env

Ubicación: `/.env` (raíz del proyecto)

### Variables Clave:

```env
# Network Configuration
SERVER_IP=192.168.137.24
SERVER_PORT=5000
FRONTEND_PORT=8080
FLASK_SERVER_URL=http://192.168.137.24:5000

# WiFi Configuration (Para Arduino)
WIFI_SSID=nombre_de_tu_red_wifi
WIFI_PASSWORD=tu_contraseña_wifi
```

---

## 🔄 Flujo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    ARCHIVO .env                              │
│  (Raíz del proyecto)                                         │
│                                                               │
│  SERVER_IP=192.168.137.24                                    │
│  WIFI_SSID=MiRedWiFi                                         │
│  WIFI_PASSWORD=mi_contraseña                                 │
│  FLASK_SERVER_URL=http://192.168.137.24:5000                │
└─────────────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────────────────┐
         │                                                     │
         ▼                                                     ▼
┌──────────────────────┐                          ┌──────────────────────┐
│   BACKEND FLASK      │                          │   ARDUINO WiFi       │
│                      │                          │                      │
│  Lee directamente    │                          │  Usa script Python  │
│  con os.getenv()     │                          │  para generar       │
│                      │                          │  wifi_config.h      │
│  Variables usadas:   │                          │                      │
│  - SERVER_IP         │                          │  Variables usadas:  │
│  - SERVER_PORT       │                          │  - WIFI_SSID        │
│  - MONGO_URI         │                          │  - WIFI_PASSWORD    │
│  - CORS_ORIGINS      │                          │  - FLASK_SERVER_URL │
└──────────────────────┘                          └──────────────────────┘
         │                                                     │
         │                                                     │
         ▼                                                     ▼
┌──────────────────────┐                          ┌──────────────────────┐
│   FRONTEND Vue.js    │                          │   wifi_config.h      │
│                      │                          │   (Generado)          │
│  Detecta automáticamente│                       │                      │
│  desde el navegador  │                          │  #define WIFI_SSID   │
│                      │                          │  #define SERVER_HOST │
│  Si es localhost:    │                          │  #define SERVER_PORT │
│  → localhost:5000     │                          │                      │
│                      │                          │  Incluido en:        │
│  Si es IP:           │                          │  nivel_agua_wifi.ino │
│  → IP:5000           │                          └──────────────────────┘
└──────────────────────┘
```

---

## 🔧 Componente 1: Backend Flask

### Cómo lee el .env:

**Archivo:** `backend/backend-flask/app/__init__.py`

```python
import os
from dotenv import load_dotenv

# Carga automáticamente el .env
load_dotenv()

# Lee variables directamente
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
```

### Variables que lee:

- `SERVER_IP` - Para logs y configuración
- `SERVER_PORT` - Puerto del servidor
- `MONGO_URI` - Conexión a MongoDB
- `MONGO_DB` - Nombre de la base de datos
- `CORS_ORIGINS` - Orígenes permitidos
- `FLASK_ENV` - Entorno (development/production)
- `FLASK_DEBUG` - Modo debug

### En Docker:

El `.env` se monta como volumen en `docker-compose.yml`:
```yaml
volumes:
  - ./.env:/app/.env:ro
```

---

## 🎨 Componente 2: Frontend Vue.js

### Cómo lee la configuración:

**Archivo:** `frontend/src/config/api.js`

El frontend **lee la configuración del backend** a través del endpoint `/api/config`:

1. **Al iniciar:** Intenta obtener configuración del backend (lee del `.env`)
2. **Endpoint:** `GET /api/config` → Devuelve `SERVER_IP`, `SERVER_PORT`, `FLASK_SERVER_URL`
3. **Fallback:** Si no puede obtener la configuración, detecta automáticamente desde el navegador

```javascript
// Intenta obtener configuración del backend (lee del .env)
const response = await fetch(`${baseUrl}/api/config`)
const config = await response.json()
// Usa: config.flask_server_url, config.server_ip, config.server_port
```

### Flujo:

```
Frontend inicia
    ↓
Intenta: GET /api/config (backend lee .env)
    ↓
Si éxito: Usa SERVER_IP y SERVER_PORT del .env
    ↓
Si falla: Detecta automáticamente desde navegador
```

### Ejemplos:

| Acceso desde | Configuración usada |
|--------------|---------------------|
| `http://localhost:8080` | Lee `.env` → `SERVER_IP=192.168.137.24` → Usa `http://192.168.137.24:5000` |
| `http://192.168.137.24:8080` | Lee `.env` → `SERVER_IP=192.168.137.24` → Usa `http://192.168.137.24:5000` |

**Ventaja:** Usa la IP del `.env` en lugar de detectar automáticamente.

---

## 🔌 Componente 3: Arduino WiFi

### Cómo lee el .env:

**Archivo:** `backend/arduino/network_config.py`

El Arduino **NO lee directamente el .env**. En su lugar, un **script Python** lee el `.env` y genera un archivo de configuración C++.

### Proceso:

#### Paso 1: Script lee .env

**Archivo:** `backend/arduino/generar_config_wifi.py`

```python
from network_config import cargar_config_red

# Lee el .env
config = cargar_config_red()

# Extrae valores
wifi_ssid = config['wifi_ssid']        # De WIFI_SSID
wifi_password = config['wifi_password'] # De WIFI_PASSWORD
flask_server_url = config['flask_server_url'] # De FLASK_SERVER_URL
```

#### Paso 2: Genera wifi_config.h

El script genera `backend/arduino/wifi_config.h`:

```cpp
#define WIFI_SSID "MiRedWiFi"
#define WIFI_PASSWORD "mi_contraseña"
#define SERVER_HOST "192.168.137.24"
#define SERVER_PORT 5000
```

#### Paso 3: Arduino usa wifi_config.h

**Archivo:** `backend/arduino/nivel_agua_wifi.ino`

```cpp
#include "wifi_config.h"

// Usa las constantes definidas
WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
String url = "http://" + String(SERVER_HOST) + ":" + String(SERVER_PORT);
```

### Variables que lee del .env:

- `WIFI_SSID` → `#define WIFI_SSID`
- `WIFI_PASSWORD` → `#define WIFI_PASSWORD`
- `FLASK_SERVER_URL` → Parsea y genera `SERVER_HOST`, `SERVER_PORT`, `USE_HTTPS`
- `SERVER_IP` (fallback) → Si no hay `FLASK_SERVER_URL`
- `SERVER_PORT` (fallback) → Si no hay `FLASK_SERVER_URL`

---

## 🚀 Cómo Usar

### 1. Configurar .env

```bash
# Copiar ejemplo
cp config/example.env .env

# Editar .env
# - SERVER_IP: Tu IP local
# - WIFI_SSID: Nombre de tu red WiFi
# - WIFI_PASSWORD: Contraseña WiFi
```

### 2. Backend Flask

**Se lee automáticamente** al iniciar:
```bash
docker compose up backend
```

No necesitas hacer nada más.

### 3. Frontend Vue.js

**Detecta automáticamente** desde el navegador.

Si accedes desde `http://192.168.137.24:8080`, automáticamente usará `http://192.168.137.24:5000` para el backend.

### 4. Arduino WiFi

**Generar configuración:**
```powershell
.\scripts\verificar-config-arduino.ps1
```

Este script:
1. ✅ Lee el `.env`
2. ✅ Valida la configuración
3. ✅ Genera `wifi_config.h`
4. ✅ Muestra resumen

**Luego sube el código al Arduino:**
- Abre `backend/arduino/nivel_agua_wifi.ino` en Arduino IDE
- Sube el código

---

## 📝 Módulo network_config.py

**Ubicación:** `backend/arduino/network_config.py`

Este módulo centraliza la lectura del `.env` para el Arduino:

### Funciones principales:

```python
# Cargar toda la configuración
config = cargar_config_red()

# Obtener URL del servidor
url = obtener_url_servidor()

# Obtener IP
ip = obtener_ip_servidor()

# Obtener credenciales WiFi
ssid, password = obtener_credenciales_wifi()

# Validar configuración
es_valida, errores = validar_config_red()

# Mostrar configuración
mostrar_config_red()
```

### Uso directo:

```bash
python backend/arduino/network_config.py
```

Muestra la configuración actual del `.env`.

---

## ✅ Verificación

### Ver configuración actual:

```powershell
# Opción 1: Script de verificación (recomendado)
.\scripts\verificar-config-arduino.ps1

# Opción 2: Módulo Python directamente
python backend\arduino\network_config.py
```

### Verificar que todo funciona:

1. **Backend:** `http://localhost:5000/api/health`
2. **Frontend:** `http://localhost:8080`
3. **Arduino:** Revisa monitor serial (debe conectarse a WiFi)

---

## 🔄 Resumen del Flujo

| Componente | Cómo lee .env | Cuándo se lee |
|------------|---------------|---------------|
| **Backend Flask** | `os.getenv()` directamente | Al iniciar el servidor |
| **Frontend Vue.js** | Detecta automáticamente desde navegador | En tiempo de ejecución (navegador) |
| **Arduino WiFi** | Script Python genera `wifi_config.h` | Al ejecutar `verificar-config-arduino.ps1` |

---

## 💡 Ventajas de este Sistema

✅ **Centralizado:** Todo en un solo archivo `.env`  
✅ **Automático:** Frontend detecta IP automáticamente  
✅ **Validado:** Scripts validan la configuración antes de usar  
✅ **Flexible:** Soporta IPs locales y URLs remotas  
✅ **Seguro:** Contraseñas en `.env` (no en código)  

---

## 🎯 Ejemplo Completo

### 1. Configurar .env:
```env
SERVER_IP=192.168.137.24
WIFI_SSID=MiCasa_WiFi
WIFI_PASSWORD=password123
FLASK_SERVER_URL=http://192.168.137.24:5000
```

### 2. Iniciar servicios:
```bash
docker compose up -d
```

### 3. Configurar Arduino:
```powershell
.\scripts\verificar-config-arduino.ps1
```

### 4. Resultado:
- ✅ Backend en `http://192.168.137.24:5000`
- ✅ Frontend en `http://192.168.137.24:8080` → se conecta automáticamente al backend
- ✅ Arduino se conecta a `MiCasa_WiFi` y envía datos a `http://192.168.137.24:5000`

---

¡Todo funciona desde un solo archivo `.env`! 🚀

