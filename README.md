# 🌊 Sistema de Alerta Temprana

Sistema de monitoreo en tiempo real del nivel de agua con alertas automáticas para prevenir inundaciones y sequías.

## 🏗️ Arquitectura

- **Backend**: Flask (Python) - API REST
- **Frontend**: Vue.js 3 + Tailwind CSS
- **Base de Datos**: MongoDB
- **Hardware**: Arduino ESP8266/ESP32 con sensor ultrasónico HC-SR04
- **Comunicación**: WiFi (HTTP/HTTPS)

## 🚀 Inicio Rápido - Desarrollo Local

### Requisitos Previos

- Docker Desktop instalado y ejecutándose
- Git

### 1. Configurar entorno

```bash
# Copiar archivo de configuración
cp config/example.env .env

# Editar .env y configurar:
# - SERVER_IP: Tu IP local
# - WIFI_SSID: Nombre de tu red WiFi
# - WIFI_PASSWORD: Contraseña de tu red WiFi
```

### 2. Iniciar servicios

```bash
docker compose up -d
```

### 3. Acceder a la aplicación

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **Mongo Express** (Admin DB): http://localhost:8081
  - Usuario: `admin` / Contraseña: `admin123`

### 4. Crear usuario administrador

```bash
docker compose exec backend python create_user.py
```

### 5. Generar códigos QR (Opcional)

Para generar códigos QR de WiFi y URL del sistema automáticamente:

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File scripts\generar-qr-completo-host.ps1
```

Este comando:
1. Detecta automáticamente tu IP de red y red WiFi actual
2. Actualiza el archivo `.env` con la configuración detectada
3. Genera códigos QR para:
   - Conectar a la red WiFi (en `qr_codes/wifi/`)
   - Acceder al sistema (en `qr_codes/url/`)
4. Reinicia los contenedores con la nueva configuración

**Nota**: Requiere permisos de administrador para obtener la contraseña WiFi automáticamente.

**📖 Ver guía completa:** [DESARROLLO_LOCAL.md](DESARROLLO_LOCAL.md)

## 🔌 Configurar Arduino WiFi

### 1. Generar configuración WiFi

```powershell
.\scripts\verificar-config-arduino.ps1
```

Este script lee `.env` y genera `backend/arduino/wifi_config.h`

### 2. Subir código al Arduino

- Abre `backend/arduino/nivel_agua_wifi.ino` en Arduino IDE
- Selecciona tu placa (ESP8266 o ESP32)
- Sube el código

**📖 Ver guía completa:** [docs/CONFIGURACION_ARDUINO_WIFI.md](docs/CONFIGURACION_ARDUINO_WIFI.md)

## 🔲 Generar Códigos QR

### Generar QR de WiFi y URL automáticamente:

```powershell
.\scripts\generar-qr.ps1
```

Este script:
- ✅ Lee el `.env` automáticamente
- ✅ Detecta la IP de la red si no está configurada
- ✅ Genera QR de WiFi (para conectar a la red)
- ✅ Genera QR de URL (para acceder al sistema)

Los QR codes se guardan en `qr_codes/`:
- `qr-wifi.png` - Escanea para conectar a WiFi
- `qr-url.png` - Escanea para acceder al sistema

**📖 Ver guía completa:** [docs/GENERAR_QR.md](docs/GENERAR_QR.md)

## 📚 Documentación

- [Desarrollo Local](DESARROLLO_LOCAL.md) - Guía completa de desarrollo local
- [Configuración WiFi Arduino](docs/CONFIGURACION_ARDUINO_WIFI.md) - Configurar Arduino WiFi
- [Generar Códigos QR](docs/GENERAR_QR.md) - Generar QR de WiFi y URL
- [Flujo de Configuración](docs/FLUJO_CONFIGURACION.md) - Cómo funciona la lectura del .env

## 🛠️ Scripts Esenciales

- `scripts/verificar-config-arduino.ps1` - Verificar y generar configuración Arduino WiFi
- `scripts/generar-qr.ps1` - Generar códigos QR (WiFi y URL) automáticamente
- `scripts/generar-secret-key.py` - Generar clave secreta para Flask

## 📝 Variables de Entorno

Configura estas variables en tu `.env`:

```env
# WiFi (para Arduino)
WIFI_SSID=nombre_de_tu_red
WIFI_PASSWORD=tu_contraseña

# URL del servidor (local)
FLASK_SERVER_URL=http://192.168.137.24:5000
```

## 🐛 Solución de Problemas

### Servicios no inician
- Verifica que Docker Desktop esté ejecutándose
- Revisa logs: `docker compose logs`
- Verifica puertos disponibles (5000, 8080, 27017)

### Arduino no se conecta
- Verifica credenciales WiFi en `.env`
- Ejecuta `.\scripts\verificar-config-arduino.ps1`
- Revisa monitor serial del Arduino

### Frontend no se conecta al backend
- Verifica que ambos servicios estén corriendo: `docker compose ps`
- Revisa la configuración en `frontend/src/config/api.js`
- Verifica CORS en el backend

## 📄 Licencia

Este proyecto es parte del Sistema de Alerta Temprana desarrollado para SENA.

## 👥 Contribuidores

- Sistema desarrollado para monitoreo de nivel de agua

---

**¿Necesitas ayuda?** Revisa la documentación en `docs/` o los scripts en `scripts/`

