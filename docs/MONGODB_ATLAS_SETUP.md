# 🗄️ Configurar MongoDB Atlas (Gratis)

Render no ofrece MongoDB gratuito, pero puedes usar **MongoDB Atlas** que tiene un plan gratuito generoso.

## 📋 Pasos para configurar MongoDB Atlas

### 1. Crear cuenta en MongoDB Atlas

1. Ve a https://www.mongodb.com/cloud/atlas
2. Crea una cuenta gratuita
3. Verifica tu email

### 2. Crear un cluster gratuito

1. En el dashboard, haz clic en **"Build a Database"**
2. Selecciona el plan **"M0 Free"** (gratis)
3. Elige una región cercana a ti
4. Haz clic en **"Create"**

### 3. Configurar acceso

1. **Crear usuario de base de datos:**
   - Ve a "Database Access"
   - Click en "Add New Database User"
   - Username: `sat_user` (o el que prefieras)
   - Password: Genera una contraseña segura
   - Database User Privileges: "Read and write to any database"
   - Click en "Add User"

2. **Configurar acceso de red:**
   - Ve a "Network Access"
   - Click en "Add IP Address"
   - Selecciona **"Allow Access from Anywhere"** (0.0.0.0/0)
   - O agrega la IP específica de Render si la conoces
   - Click en "Confirm"

### 4. Obtener Connection String

1. Ve a "Database" → "Connect"
2. Selecciona "Connect your application"
3. Driver: **Python** (versión 3.6 o superior)
4. Copia la connection string

Formato:
```
mongodb+srv://sat_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**Importante:** Reemplaza `<password>` con la contraseña que creaste.

### 5. Configurar en Render

1. Ve a tu servicio `sat-backend` en Render
2. Ve a "Environment"
3. Agrega o edita la variable `MONGO_URI`:
   ```
   mongodb+srv://sat_user:TU_PASSWORD@cluster0.xxxxx.mongodb.net/sat_database?retryWrites=true&w=majority
   ```
   **Nota:** Agrega `/sat_database` antes del `?` para especificar la base de datos.

4. Guarda los cambios
5. Render reiniciará automáticamente el servicio

## ✅ Verificar conexión

Una vez configurado, verifica que el backend se conecte correctamente:

1. Ve a los logs de `sat-backend` en Render
2. Deberías ver mensajes de conexión exitosa a MongoDB
3. Si hay errores, verifica:
   - Que la contraseña esté correcta (sin `<` y `>`)
   - Que el acceso de red esté configurado (0.0.0.0/0)
   - Que el usuario tenga permisos correctos

## 🔒 Seguridad

- **Nunca** commitees la connection string en el código
- Usa variables de entorno siempre
- Considera restringir el acceso de red a solo las IPs de Render en producción

## 📊 Límites del plan gratuito

- **512 MB de almacenamiento** (suficiente para desarrollo)
- **Shared RAM y vCPU**
- **Ideal para:** Desarrollo, pruebas, proyectos pequeños

---

¡Listo! Tu aplicación ahora usa MongoDB Atlas gratuito. 🎉

