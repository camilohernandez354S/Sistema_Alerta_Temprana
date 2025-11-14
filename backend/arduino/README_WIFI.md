# Configuración WiFi para Arduino ESP8266/ESP32

Este directorio contiene los archivos necesarios para conectar el Arduino ESP8266/ESP32 a WiFi y enviar datos directamente al servidor Flask.

## Archivos

- `nivel_agua_wifi.ino`: Código del Arduino con soporte WiFi
- `generar_config_wifi.py`: Script para generar configuración WiFi desde .env
- `wifi_config.h`: Archivo de configuración generado automáticamente (no editar manualmente)

## Requisitos

1. **Hardware:**
   - ESP8266 o ESP32
   - Sensor ultrasónico HC-SR04
   - LEDs y buzzer (opcional)

2. **Software:**
   - Arduino IDE con soporte para ESP8266/ESP32
   - Python 3 con `python-dotenv` instalado

## Instalación

### 1. Instalar librerías en Arduino IDE

Abre Arduino IDE y ve a:
- **Herramientas → Administrar librerías**
- Busca e instala:
  - `ESP8266WiFi` (para ESP8266)
  - `WiFi` (para ESP32, viene incluido)
  - `HTTPClient` (viene incluido)

### 2. Configurar credenciales WiFi en `.env`

El Arduino WiFi usa **automáticamente** las siguientes variables del archivo `.env`:

```env
# WiFi Configuration (Para Arduino ESP8266/ESP32)
WIFI_SSID=nombre_de_tu_red_wifi
WIFI_PASSWORD=tu_contraseña_wifi

# URL del servidor Flask (puede ser IP local o URL remota)
FLASK_SERVER_URL=http://192.168.137.24:5000
# O para producción remota:
# FLASK_SERVER_URL=https://sat-backend.onrender.com
```

**Notas:**
- El script `generar_config_wifi.py` lee estas variables del `.env`
- Si `FLASK_SERVER_URL` no está definido, se genera desde `SERVER_IP` y `SERVER_PORT`
- Soporta tanto IPs locales (`http://192.168.x.x:5000`) como URLs remotas (`https://...`)

### 3. Generar configuración WiFi

El script lee automáticamente el `.env` y genera `wifi_config.h`:

**Opción A - Script de verificación (recomendado):**
```powershell
.\scripts\verificar-config-arduino.ps1
```

**Opción B - Directamente:**
```bash
cd backend/arduino
python generar_config_wifi.py
```

**Opción C - Desde la raíz del proyecto:**
```powershell
python backend\arduino\generar_config_wifi.py
```

Esto generará el archivo `wifi_config.h` con:
- ✅ Credenciales WiFi desde `WIFI_SSID` y `WIFI_PASSWORD`
- ✅ URL del servidor desde `FLASK_SERVER_URL` (o `SERVER_IP` + `SERVER_PORT`)
- ✅ Soporte automático para HTTPS si la URL es `https://`

### 4. Subir código al Arduino

1. Abre `nivel_agua_wifi.ino` en Arduino IDE
2. Selecciona tu placa:
   - **Herramientas → Placa → ESP8266 Boards → NodeMCU 1.0** (para ESP8266)
   - **Herramientas → Placa → ESP32 Arduino → ESP32 Dev Module** (para ESP32)
3. Selecciona el puerto COM correcto
4. Haz clic en **Subir**

## Configuración de Pines

Ajusta los pines en `nivel_agua_wifi.ino` según tu conexión:

```cpp
#define TRIG_PIN 5      // Pin de trigger del sensor
#define ECHO_PIN 4      // Pin de echo del sensor
#define BUZZER_PIN 12   // Pin del buzzer
#define LED_ROJO 14     // LED rojo
#define LED_AMARILLO 13 // LED amarillo
#define LED_VERDE 15    // LED verde
```

## Funcionamiento

1. El Arduino se conecta automáticamente a la red WiFi configurada
2. Cada 5 segundos toma una lectura del sensor
3. Clasifica el estado (Inundación, Normal, Sequía)
4. Envía los datos al servidor Flask mediante HTTP POST
5. Actualiza los LEDs y buzzer según el estado

## Monitoreo Serial

Abre el Monitor Serial en Arduino IDE (115200 baudios) para ver:
- Estado de conexión WiFi
- Lecturas del sensor
- Respuestas del servidor
- Errores de conexión

## Solución de Problemas

### No se conecta a WiFi
- Verifica que `WIFI_SSID` y `WIFI_PASSWORD` estén correctos en el `.env`
- Ejecuta `generar_config_wifi.py` nuevamente
- Verifica que la red WiFi esté disponible

### No envía datos al servidor
- Verifica que `FLASK_SERVER_URL` sea correcto en el `.env`
- Asegúrate de que el servidor Flask esté corriendo
- Revisa el Monitor Serial para ver errores HTTP

### Error al compilar
- Verifica que tengas las librerías correctas instaladas
- Asegúrate de haber seleccionado la placa correcta (ESP8266 o ESP32)

## Actualizar Configuración

Si cambias las credenciales WiFi en el `.env`, simplemente ejecuta:

```bash
python generar_config_wifi.py
```

Y vuelve a subir el código al Arduino.

