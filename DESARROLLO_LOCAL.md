# 🚀 Desarrollo Local con Docker

## 📋 Requisitos Previos

- Docker Desktop instalado y ejecutándose
- Git (para clonar el repositorio)

## ⚙️ Configuración Inicial

### 1. Crear archivo `.env`

Copia el archivo de ejemplo y configura tus valores:

```bash
cp config/example.env .env
```

Edita `.env` y configura:
- `SERVER_IP`: Tu IP local (ej: `192.168.137.24`)
- `WIFI_SSID`: Nombre de tu red WiFi (para Arduino)
- `WIFI_PASSWORD`: Contraseña de tu red WiFi

### 2. Verificar configuración

```powershell
# Windows PowerShell
.\scripts\verificar-config-arduino.ps1
```

## 🐳 Iniciar Servicios

### Iniciar todos los servicios:

```bash
docker compose up -d
```

### Ver logs en tiempo real:

```bash
docker compose up
```

### Detener servicios:

```bash
docker compose down
```

### Detener y eliminar volúmenes (limpiar base de datos):

```bash
docker compose down -v
```

## 🌐 URLs de Acceso

Una vez iniciados los servicios:

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health
- **Mongo Express** (Admin DB): http://localhost:8081
  - Usuario: `admin`
  - Contraseña: `admin123`

## 📱 Acceso desde Red Local

Para acceder desde tu teléfono u otro dispositivo en la misma red:

1. Obtén tu IP local:
   ```powershell
   ipconfig | findstr /i "IPv4"
   ```

2. Accede desde el navegador:
   - Frontend: `http://TU_IP:8080`
   - Backend: `http://TU_IP:5000`

## 🔧 Comandos Útiles

### Ver logs de un servicio específico:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mongo
```

### Reiniciar un servicio:

```bash
docker compose restart backend
docker compose restart frontend
```

### Reconstruir imágenes:

```bash
docker compose up -d --build
```

### Ejecutar comandos dentro de un contenedor:

```bash
# Backend
docker compose exec backend python create_user.py

# Frontend
docker compose exec frontend npm install
```

## 🗄️ Base de Datos

### Crear usuario administrador:

```bash
docker compose exec backend python create_user.py
```

### Migrar base de datos:

```bash
docker compose exec backend python migrate.py
```

## 🔌 Arduino

### Configurar Arduino para WiFi:

```powershell
.\scripts\verificar-config-arduino.ps1
```

Esto generará `backend/arduino/wifi_config.h` con la configuración desde `.env`.

### Arduino Serial (Local):

Si usas Arduino por puerto serial (no WiFi), configura en `.env`:
```env
ARDUINO_PORT=COM11
ARDUINO_BAUDRATE=9600
ARDUINO_ENABLED=True
```

## 🐛 Solución de Problemas

### Puerto ya en uso:

Si un puerto está ocupado, detén el servicio que lo usa o cambia el puerto en `docker-compose.yml`.

### Error de conexión a MongoDB:

Verifica que el servicio `mongo` esté corriendo:
```bash
docker compose ps
```

### Frontend no se conecta al backend:

1. Verifica que ambos servicios estén corriendo
2. Revisa la configuración en `frontend/src/config/api.js`
3. Verifica CORS en el backend

### Limpiar todo y empezar de nuevo:

```bash
docker compose down -v
docker system prune -a
docker compose up -d --build
```

## 📝 Notas

- Los cambios en el código se reflejan automáticamente (volúmenes montados)
- La base de datos persiste en el volumen `mongo_data`
- Para producción, usa `gunicorn` en lugar de `run.py`

## ✅ Verificación

1. ✅ Backend responde: http://localhost:5000/api/health
2. ✅ Frontend carga: http://localhost:8080
3. ✅ MongoDB accesible: http://localhost:8081
4. ✅ Logs sin errores: `docker compose logs`

¡Listo para desarrollar! 🎉

