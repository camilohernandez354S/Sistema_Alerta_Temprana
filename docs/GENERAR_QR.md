# 🔲 Generar Códigos QR

## 📋 Resumen

El sistema puede generar automáticamente dos tipos de códigos QR:

1. **QR de WiFi** - Para conectar automáticamente a la red WiFi
2. **QR de URL** - Para acceder rápidamente al sistema desde el teléfono

---

## 🚀 Generar Ambos QR Automáticamente

### Opción 1: Script Completo (Recomendado)

Este script:
- ✅ Lee el `.env` automáticamente
- ✅ Detecta la IP de la red si no está en `.env`
- ✅ Genera ambos QR codes

**PowerShell:**
```powershell
.\scripts\generar-qr.ps1
```

**Batch:**
```cmd
scripts\generar-qr.bat
```

**Python directo:**
```bash
python scripts\generar-qr-completo.py
```

### Opción 2: Scripts Individuales

**Solo QR de WiFi:**
```bash
python scripts\generar-qr-wifi.py
```

**Solo QR de URL:**
```bash
python scripts\generar-qr-url.py
```

---

## 📁 Archivos Generados

Los QR codes se guardan en `qr_codes/`:

- `qr-wifi.png` - Código QR para conectar a WiFi
- `qr-url.png` - Código QR para acceder al sistema

---

## 🔧 Cómo Funciona

### QR de WiFi

**Formato:** `WIFI:T:WPA;S:ASUS;P:20051322;;`

- Al escanear con el teléfono, se conecta automáticamente a la red WiFi
- Lee `WIFI_SSID` y `WIFI_PASSWORD` del `.env`

### QR de URL

**Formato:** `http://192.168.137.24:8080`

- Al escanear con el teléfono, abre el sistema en el navegador
- Lee `SERVER_IP` y `FRONTEND_PORT` del `.env`
- Si no hay IP en `.env`, la detecta automáticamente

---

## 🔍 Detección Automática de IP

El script `generar-qr-completo.py` puede detectar tu IP automáticamente:

1. **Si `SERVER_IP` está en `.env`:** Usa esa IP
2. **Si no está o es `localhost`:** Detecta la IP de la red automáticamente
3. **Muestra la IP detectada:** Para que puedas actualizar el `.env` si quieres

---

## 📝 Requisitos

- Python 3.7+
- Dependencias instaladas:
  ```bash
  pip install qrcode[pil] python-dotenv
  ```

---

## 💡 Uso

### Escenario 1: Primera vez

1. Configura tu `.env` con:
   ```env
   SERVER_IP=192.168.137.24
   WIFI_SSID=ASUS
   WIFI_PASSWORD=20051322
   FRONTEND_PORT=8080
   ```

2. Ejecuta:
   ```powershell
   .\scripts\generar-qr.ps1
   ```

3. Los QR codes estarán en `qr_codes/`

### Escenario 2: IP automática

1. Ejecuta el script (aunque no tengas `SERVER_IP` en `.env`):
   ```powershell
   .\scripts\generar-qr.ps1
   ```

2. El script detectará tu IP automáticamente

3. Actualiza el `.env` con la IP detectada si quieres

---

## 🎯 Ejemplo de Salida

```
============================================================
🔲 GENERANDO CÓDIGOS QR
============================================================

📍 IP detectada automáticamente: 192.168.137.24

📋 Generando QR codes...

✅ QR WiFi: qr_codes\qr-wifi.png
✅ QR URL: qr_codes\qr-url.png
🌐 URL: http://192.168.137.24:8080

============================================================
✅ ¡CÓDIGOS QR GENERADOS EXITOSAMENTE!
============================================================

📁 Archivos guardados en: qr_codes/
   - qr-wifi.png (conectar a WiFi)
   - qr-url.png (acceder al sistema)
```

---

## 📱 Cómo Usar los QR

### QR de WiFi

1. Abre la cámara del teléfono
2. Escanea `qr-wifi.png`
3. Toca la notificación que aparece
4. Se conecta automáticamente a la red WiFi

### QR de URL

1. Abre la cámara del teléfono
2. Escanea `qr-url.png`
3. Toca la notificación que aparece
4. Se abre el sistema en el navegador

---

## 🔄 Actualizar QR Codes

Si cambias la configuración en `.env`, simplemente vuelve a ejecutar:

```powershell
.\scripts\generar-qr.ps1
```

Los QR codes se regenerarán con la nueva configuración.

---

## ⚠️ Notas

- Los QR codes se guardan en `qr_codes/` (no se suben a Git)
- Si cambias la IP, regenera los QR codes
- El QR de WiFi solo funciona si el teléfono soporta conexión WiFi automática

---

¡Listo! Ahora puedes generar QR codes fácilmente. 🚀

