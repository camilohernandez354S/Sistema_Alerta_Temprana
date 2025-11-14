# 🌊 Sistema de Alerta Temprana

Sistema de monitoreo en tiempo real del nivel de agua con alertas automáticas para prevenir inundaciones y sequías.

## 🏗️ Arquitectura

- **Backend**: Flask (Python) - API REST
- **Frontend**: Vue.js 3 + Tailwind CSS
- **Base de Datos**: MongoDB
- **Hardware**: Arduino ESP8266/ESP32 con sensor ultrasónico HC-SR04
- **Comunicación**: WiFi (HTTP/HTTPS)

## 🚀 Despliegue en Render

**Despliegue remoto desde la terminal:**

1. **Configurar API Key de Render**
```powershell
.\scripts\configurar-render-api-key.ps1
```

2. **Subir código a GitHub**
```bash
git add .
git commit -m "Configuración para Render"
git push origin main
```

3. **Crear servicios en Render (primera vez)**
   - Ve a https://dashboard.render.com
   - New → Blueprint
   - Conecta tu repositorio
   - Render detectará `render.yaml` automáticamente

4. **Desplegar desde terminal**
```powershell
.\scripts\desplegar-render.ps1 -All
```

**📖 Ver guía completa:** [docs/DESPLIEGUE_TERMINAL.md](docs/DESPLIEGUE_TERMINAL.md)

### Configurar Arduino WiFi

Una vez desplegado en Render, configura el Arduino para usar la URL remota:

1. **Configurar Arduino para producción**
```powershell
.\scripts\configurar-arduino-remoto.ps1
```

Este script te pedirá la URL de tu backend en Render (ej: `https://sat-backend.onrender.com`)

2. **Generar configuración WiFi**
```powershell
.\scripts\verificar-config-arduino.ps1
```

3. **Subir código al Arduino**
- Abre `backend/arduino/nivel_agua_wifi.ino` en Arduino IDE
- Selecciona tu placa (ESP8266 o ESP32)
- Sube el código

**📖 Ver guía completa:** [docs/CONFIGURACION_ARDUINO_WIFI.md](docs/CONFIGURACION_ARDUINO_WIFI.md)


## 📚 Documentación

- [Despliegue desde Terminal](docs/DESPLIEGUE_TERMINAL.md) - Guía completa de despliegue
- [Configuración WiFi Arduino](docs/CONFIGURACION_ARDUINO_WIFI.md) - Configurar Arduino para producción

## 🛠️ Scripts Esenciales

- `scripts/configurar-render-api-key.ps1` - Configurar API Key de Render (primera vez)
- `scripts/desplegar-render.ps1` - Desplegar en Render desde terminal
- `scripts/configurar-arduino-remoto.ps1` - Configurar Arduino para producción
- `scripts/verificar-config-arduino.ps1` - Verificar configuración Arduino
- `scripts/generar-secret-key.py` - Generar clave secreta para Flask

## 📝 Variables de Entorno para Arduino

Configura estas variables en tu `.env` local para el Arduino:

```env
# WiFi (para Arduino)
WIFI_SSID=nombre_de_tu_red
WIFI_PASSWORD=tu_contraseña

# URL del servidor en Render
FLASK_SERVER_URL=https://sat-backend.onrender.com
```

## 🐛 Solución de Problemas

### Arduino no se conecta
- Verifica credenciales WiFi en `.env`
- Ejecuta `.\scripts\verificar-config-arduino.ps1`
- Revisa monitor serial del Arduino

### Error de despliegue en Render
- Verifica que `render.yaml` esté correcto
- Revisa los logs en el dashboard de Render
- Asegúrate de que todas las variables de entorno estén configuradas

## 📄 Licencia

Este proyecto es parte del Sistema de Alerta Temprana desarrollado para SENA.

## 👥 Contribuidores

- Sistema desarrollado para monitoreo de nivel de agua

---

**¿Necesitas ayuda?** Revisa la documentación en `docs/` o los scripts en `scripts/`

