# Instrucciones para usar leer_serial.py

## Requisitos previos

Este script necesita las siguientes dependencias de Python:

1. **pyserial** - Para comunicación serial con Arduino/ESP8266
2. **python-dotenv** - Para cargar variables de entorno
3. **requests** - Para enviar datos al servidor Flask

## Instalación de dependencias

### Opción 1: Script automático (Windows)

```bash
instalar_dependencias.bat
```

### Opción 2: Script automático (Linux/Mac)

```bash
chmod +x instalar_dependencias.sh
./instalar_dependencias.sh
```

### Opción 3: Instalación manual

#### En Windows:
```bash
py -m pip install pyserial python-dotenv requests
```

#### En Linux/Mac:
```bash
python3 -m pip install pyserial python-dotenv requests
```

## Configuración

1. **Crear archivo `.env`** en `backend/backend-flask/` con:

```env
SERIAL_PORT=COM7
BAUD_RATE=115200
FLASK_SERVER_URL=http://localhost:5000
```

**Nota:** Ajusta `SERIAL_PORT` según tu sistema:
- Windows: `COM3`, `COM4`, `COM7`, etc.
- Linux/Mac: `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.

## Ejecutar el script

### Windows:
```bash
py leer_serial.py
```

### Linux/Mac:
```bash
python3 leer_serial.py
```

## Ver puertos seriales disponibles

El script mostrará automáticamente los puertos disponibles si hay un error.

También puedes verificar manualmente:

### Windows:
```bash
py -c "import serial.tools.list_ports; [print(p.device) for p in serial.tools.list_ports.comports()]"
```

### Linux/Mac:
```bash
ls /dev/tty* | grep -E "(USB|ACM)"
```

## Solución de problemas

### Error: "ModuleNotFoundError: No module named 'serial'"
**Solución:** Instala pyserial:
```bash
py -m pip install pyserial
```

### Error: "No se pudo conectar al puerto"
**Soluciones:**
1. Verifica que el puerto esté correcto en `.env`
2. Cierra Arduino IDE o cualquier otro programa que use el puerto
3. Verifica que el dispositivo esté conectado

### Error: "Error del servidor"
**Soluciones:**
1. Verifica que el servidor Flask esté corriendo
2. Verifica la URL en `FLASK_SERVER_URL` en el `.env`
3. Verifica que el backend Flask esté accesible

## Formato de datos esperado

El script espera recibir datos en formato:
```
TIMESTAMP:12345,NIVEL:25.50,ESTADO:Normal
```

Este formato es compatible con:
- `nivel_agua.ino` (Arduino tradicional)
- `esp8266_nivel_agua.ino` (ESP8266 con WiFi)
- `esp_config.ino` (ESP8266 integrado)

