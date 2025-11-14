# 🚀 Despliegue en Render desde la Terminal

## 📋 Resumen

Esta guía te permite desplegar tu aplicación en Render directamente desde la terminal, sin necesidad de usar la interfaz web.

---

## 🔑 Paso 1: Configurar API Key de Render

### Opción A: Script Automático (Recomendado)

```powershell
.\scripts\configurar-render-api-key.ps1
```

Este script te guiará para:
1. Obtener tu API Key de Render
2. Configurarla en tu sesión actual
3. Opcionalmente guardarla en tu perfil de PowerShell

### Opción B: Manual

1. **Obtener API Key:**
   - Ve a https://dashboard.render.com/account/api-keys
   - Inicia sesión
   - Crea una nueva API Key
   - Copia la key generada

2. **Configurar en PowerShell:**
   ```powershell
   $env:RENDER_API_KEY = 'tu_api_key_aqui'
   ```

3. **Guardar permanentemente (opcional):**
   ```powershell
   # Agregar al perfil de PowerShell
   Add-Content -Path $PROFILE -Value "`$env:RENDER_API_KEY = 'tu_api_key_aqui'"
   ```

---

## 🚀 Paso 2: Configurar Servicios en Render (Primera Vez)

**Nota:** La primera vez, debes crear los servicios desde la interfaz web de Render o usando `render.yaml`.

### Opción A: Desde render.yaml (Recomendado)

1. **Subir código a GitHub:**
   ```powershell
   git add .
   git commit -m "Configuración para Render"
   git push origin main
   ```

2. **En Render Dashboard:**
   - Ve a https://dashboard.render.com
   - Click en "New" → "Blueprint"
   - Conecta tu repositorio de GitHub
   - Render detectará automáticamente `render.yaml`
   - Click en "Apply"

### Opción B: Crear Servicios Manualmente

1. **Backend:**
   - New → Web Service
   - Conecta tu repositorio
   - Configura según `render.yaml`
   - Nombre: `sat-backend`

2. **Frontend:**
   - New → Static Site
   - Conecta tu repositorio
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Nombre: `sat-frontend`

3. **MongoDB:**
   - New → Database
   - MongoDB
   - Nombre: `sat-mongo`

---

## 🎯 Paso 3: Desplegar desde la Terminal

### Desplegar Todo

```powershell
.\scripts\desplegar-render.ps1 -All
```

### Desplegar Solo Backend

```powershell
.\scripts\desplegar-render.ps1 -Backend
```

### Desplegar Solo Frontend

```powershell
.\scripts\desplegar-render.ps1 -Frontend
```

---

## 📝 Ejemplo Completo

```powershell
# 1. Configurar API Key (solo la primera vez)
.\scripts\configurar-render-api-key.ps1

# 2. Verificar cambios
git status

# 3. Hacer commit y push (si hay cambios)
git add .
git commit -m "Actualización"
git push origin main

# 4. Desplegar
.\scripts\desplegar-render.ps1 -All
```

---

## 🔍 Verificar Estado del Despliegue

### Desde la Terminal

```powershell
# Ver logs del backend
curl -H "Authorization: Bearer $env:RENDER_API_KEY" \
  https://api.render.com/v1/services/{backend_service_id}/deploys

# Ver logs del frontend
curl -H "Authorization: Bearer $env:RENDER_API_KEY" \
  https://api.render.com/v1/services/{frontend_service_id}/deploys
```

### Desde el Dashboard

Ve a https://dashboard.render.com y revisa el estado de tus servicios.

---

## ⚙️ Configuración de Variables de Entorno

Las variables de entorno se configuran en `render.yaml` o desde el dashboard.

### Variables Importantes:

**Backend:**
- `FLASK_ENV=production`
- `SECRET_KEY` (generar con `.\scripts\generar-secret-key.py`)
- `MONGO_URI` (se configura automáticamente desde la base de datos)
- `CORS_ORIGINS=https://sat-frontend.onrender.com`
- `FLASK_SERVER_URL=https://sat-backend.onrender.com`

**Frontend:**
- `VITE_API_URL=https://sat-backend.onrender.com`

---

## 🐛 Solución de Problemas

### Error: "RENDER_API_KEY no está configurada"
**Solución:** Ejecuta `.\scripts\configurar-render-api-key.ps1`

### Error: "Servicio no encontrado"
**Solución:** Asegúrate de haber creado los servicios en Render primero (ver Paso 2)

### Error: "401 Unauthorized"
**Solución:** Tu API Key es inválida o expiró. Genera una nueva.

### El despliegue falla
**Solución:**
1. Revisa los logs en https://dashboard.render.com
2. Verifica que `render.yaml` esté correcto
3. Asegúrate de que todas las variables de entorno estén configuradas

---

## 📚 Comandos Útiles

### Ver servicios disponibles

```powershell
$headers = @{
    "Authorization" = "Bearer $env:RENDER_API_KEY"
    "Accept" = "application/json"
}
Invoke-RestMethod -Uri "https://api.render.com/v1/services" -Headers $headers
```

### Ver estado de un despliegue

```powershell
$serviceId = "tu_service_id"
$headers = @{
    "Authorization" = "Bearer $env:RENDER_API_KEY"
    "Accept" = "application/json"
}
Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/deploys" -Headers $headers
```

---

## 🎯 Flujo de Trabajo Recomendado

1. **Desarrollo Local:**
   - Trabaja en tu código
   - Prueba localmente con Docker

2. **Antes de Desplegar:**
   - Verifica que todo funcione localmente
   - Haz commit y push a GitHub

3. **Desplegar:**
   ```powershell
   .\scripts\desplegar-render.ps1 -All
   ```

4. **Verificar:**
   - Revisa el dashboard de Render
   - Prueba la aplicación desplegada
   - Revisa los logs si hay problemas

---

## 🔄 Actualización Continua

Si tienes auto-deploy habilitado en Render (recomendado), cada push a `main` desplegará automáticamente. Solo necesitas el script de despliegue manual si:

- Quieres forzar un despliegue sin hacer push
- Quieres desplegar un branch específico
- Quieres limpiar la caché antes de desplegar

---

## 📖 Referencias

- [Render API Documentation](https://render.com/docs/api)
- [Render Dashboard](https://dashboard.render.com)
- [Guía de Despliegue Remoto](./GUIA_DESPLIEGUE_REMOTO.md)

---

## ✅ Checklist de Despliegue

- [ ] API Key de Render configurada
- [ ] Servicios creados en Render (backend, frontend, MongoDB)
- [ ] Variables de entorno configuradas
- [ ] Código subido a GitHub
- [ ] `render.yaml` actualizado
- [ ] Despliegue ejecutado
- [ ] Aplicación funcionando en producción
- [ ] Arduino configurado con URL remota (si aplica)

---

¡Listo para desplegar! 🚀

