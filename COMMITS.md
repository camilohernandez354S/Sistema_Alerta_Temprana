# Comandos Git para Commits Separados

## ✅ 1. Arduino (YA HECHO)
```bash
git add backend/arduino/README_WIFI.md backend/arduino/network_config.py backend/arduino/update_env.py docs/CONFIGURACION_ARDUINO_WIFI.md
git commit -m "feat(arduino): actualizar configuración WiFi y documentación"
```

## 2. Scripts de generación de QR
```bash
git add scripts/generar-qr-wifi.py scripts/generar-qr-url.py scripts/generar-qr-completo.py scripts/generar-qr.ps1 scripts/generar-qr.bat
git commit -m "feat(scripts): agregar scripts de generación de códigos QR

- Agregar generar-qr-wifi.py para QR de WiFi
- Agregar generar-qr-url.py para QR de URL del sistema
- Agregar generar-qr-completo.py para generar ambos
- Agregar scripts PowerShell y Batch para ejecución fácil"
```

## 3. Scripts de detección y actualización de red
```bash
git add scripts/actualizar-config-red.ps1 scripts/actualizar-config-red-simple.ps1 scripts/detectar-red-host.py scripts/detectar-red-wifi.ps1 scripts/detectar-y-actualizar.ps1 scripts/generar-qr-completo-host.ps1 scripts/generar-qr-wifi-host.ps1
git commit -m "feat(scripts): agregar scripts de detección automática de red

- Agregar actualizar-config-red.ps1 para detectar IP y WiFi del host
- Agregar detectar-red-host.py para detección desde Python
- Agregar generar-qr-completo-host.ps1 para proceso completo
- Detección automática de red WiFi y actualización del .env"
```

## 4. Docker Compose y configuración
```bash
git add docker-compose.yml
git commit -m "feat(docker): agregar docker-compose.yml para desarrollo local

- Configurar servicios: mongo, backend, frontend, mongo-express
- Montar volúmenes para desarrollo
- Configurar red interna entre servicios"
```

## 5. Backend - Health routes y utilidades
```bash
git add backend/backend-flask/app/api/health_routes.py backend/backend-flask/create_user.py backend/backend-flask/migrate.py backend/backend-flask/.dockerignore
git commit -m "feat(backend): agregar endpoint de configuración y utilidades

- Agregar endpoint /api/config para exponer configuración del servidor
- Agregar create_user.py para crear usuarios
- Agregar migrate.py para migraciones de base de datos
- Actualizar .dockerignore"
```

## 6. Frontend - Configuración y vistas
```bash
git add frontend/src/config/api.js frontend/src/views/DashboardAdmin.vue frontend/.dockerignore frontend/nginx.conf frontend/clean-node-modules.ps1 frontend/remove-node-modules.ps1
git commit -m "feat(frontend): actualizar configuración API y vistas

- Actualizar api.js para detectar URL del backend dinámicamente
- Mejorar DashboardAdmin con diseño responsive
- Agregar nginx.conf para producción
- Agregar scripts de limpieza de node_modules"
```

## 7. Documentación
```bash
git add DESARROLLO_LOCAL.md docs/FLUJO_CONFIGURACION.md docs/GENERAR_QR.md docs/GENERAR_QR_CODES.md README.md
git commit -m "docs: agregar documentación de desarrollo local y QR codes

- Agregar DESARROLLO_LOCAL.md con guía completa
- Agregar FLUJO_CONFIGURACION.md explicando el flujo del .env
- Agregar GENERAR_QR.md y GENERAR_QR_CODES.md
- Actualizar README.md con nuevas secciones"
```

## 8. Limpieza - Eliminar archivos de Render
```bash
git add DEPLOYMENT_CONFIG.md DEPLOYMENT_GUIDE.md render.yaml scripts/configurar-arduino-remoto.bat scripts/configurar-arduino-remoto.ps1 scripts/configurar-render-api-key.ps1 scripts/desplegar-render.bat scripts/desplegar-render.ps1 docs/DESPLIEGUE_TERMINAL.md docs/MONGODB_ATLAS_SETUP.md
git commit -m "chore: eliminar archivos relacionados con despliegue remoto

- Eliminar configuración de Render (render.yaml)
- Eliminar scripts de despliegue remoto
- Eliminar documentación de MongoDB Atlas y despliegue terminal
- Enfocar proyecto en desarrollo local con Docker"
```

## 9. .env (ignorar - no se debe commitear)
```bash
# NO hacer commit del .env - está en .gitignore
# git restore .env  # para descartar cambios si es necesario
```

