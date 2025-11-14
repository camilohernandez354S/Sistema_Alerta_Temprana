# 📱 Generar Códigos QR

Este documento explica cómo generar códigos QR para facilitar el acceso al sistema y a la red WiFi.

## 🎯 ¿Qué hace el script?

El script `generar-qr-completo-host.ps1` automatiza todo el proceso:

1. **Detecta la configuración de red**:
   - IP de la red local
   - Red WiFi actual (SSID)
   - Contraseña WiFi (si está guardada en el perfil)

2. **Actualiza el archivo `.env`** automáticamente con:
   - `SERVER_IP`: IP detectada
   - `FLASK_SERVER_URL`: URL completa del backend
   - `WIFI_SSID`: Red WiFi detectada
   - `WIFI_PASSWORD`: Contraseña WiFi (si se pudo obtener)

3. **Genera códigos QR**:
   - QR de WiFi: Para conectar dispositivos a la red automáticamente
   - QR de URL: Para acceder al sistema desde cualquier dispositivo

4. **Reinicia los contenedores** con la nueva configuración

## 🚀 Uso

### Requisitos Previos

1. **Docker Desktop** debe estar ejecutándose
2. **Contenedores activos**: Ejecuta `docker compose up -d` primero
3. **Archivo `.env`** debe existir (copia de `config/example.env`)

### Ejecutar el Script

Desde la raíz del proyecto, ejecuta:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\generar-qr-completo-host.ps1
```

### Permisos de Administrador

El script intenta obtener la contraseña WiFi automáticamente desde los perfiles guardados de Windows. Esto requiere permisos de administrador.

Si no tienes permisos de administrador:
- El script detectará la red WiFi pero no la contraseña
- Deberás actualizar `WIFI_PASSWORD` manualmente en el `.env`

## 📁 Archivos Generados

Los códigos QR se guardan en:

- **WiFi**: `qr_codes/wifi/qr-wifi-[NOMBRE_RED].png`
- **URL**: `qr_codes/url/qr-url-[IP].png`

Ejemplo:
- `qr_codes/wifi/qr-wifi-MiRed.png`
- `qr_codes/url/qr-url-192-168-1-100.png`

## 🔍 Verificar Configuración

Para ver la configuración actual sin generar QR codes:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\actualizar-config-red.ps1
```

Este script solo detecta y actualiza el `.env`, sin generar QR codes.

## ⚠️ Solución de Problemas

### Error: "Docker no está disponible"

- Asegúrate de que Docker Desktop esté ejecutándose
- Verifica que los contenedores estén activos: `docker compose ps`

### Error: "No se pudo detectar red WiFi"

- Asegúrate de estar conectado a una red WiFi
- En Windows, verifica con: `netsh wlan show interfaces`

### Error: "No se pudo obtener contraseña WiFi"

- Ejecuta PowerShell como administrador
- O actualiza `WIFI_PASSWORD` manualmente en el `.env`

### Los QR codes no se generan

- Verifica que los contenedores estén activos: `docker compose ps`
- Revisa los logs: `docker compose logs backend`
- Asegúrate de que el archivo `.env` existe y tiene los valores correctos

## 📝 Notas

- Los códigos QR se generan dentro del contenedor Docker
- Los archivos se guardan en `qr_codes/` en la raíz del proyecto
- El directorio `qr_codes/` está en `.gitignore`, así que no se subirá al repositorio
- Cada vez que cambies de red WiFi, ejecuta el script nuevamente para actualizar la configuración

