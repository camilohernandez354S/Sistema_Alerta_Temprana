# 🔧 Configuración de CORS Actualizada

## ✅ Cambios Realizados

Se ha actualizado la configuración de CORS en el backend Flask para permitir peticiones desde el frontend de Vite que corre en `http://localhost:5173`.

### Archivos Modificados:

1. **`app/__init__.py`**: Agregado soporte para puertos 5173
2. **`config/config.py`**: Actualizada configuración base de CORS
3. **`env.example`**: Actualizado ejemplo de variables de entorno

### Puertos CORS Soportados:

- ✅ `http://localhost:8080` (Vue CLI)
- ✅ `http://127.0.0.1:8080` (Vue CLI)
- ✅ `http://localhost:5173` (Vite) **← NUEVO**
- ✅ `http://127.0.0.1:5173` (Vite) **← NUEVO**

## 🚀 Cómo Aplicar los Cambios

### 1. Reiniciar el Backend Flask

```bash
# Navegar al directorio del backend
cd backend/backend-flask

# Si tienes un proceso corriendo, detenerlo (Ctrl+C)
# Luego reiniciar:
python run.py
```

### 2. Verificar que Flask-CORS está Instalado

```bash
# Activar el entorno virtual
cd backend/backend-flask
source venv/Scripts/activate  # En Windows
# o
source venv/bin/activate      # En Linux/Mac

# Verificar instalación
pip show flask-cors
```

Si no está instalado:
```bash
pip install flask-cors
```

### 3. Configurar Variables de Entorno (Opcional)

Si tienes un archivo `.env`, asegúrate de que incluya:

```env
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173
```

### 4. Verificar que Funciona

1. **Iniciar el backend Flask**:
   ```bash
   cd backend/backend-flask
   python run.py
   ```
   
2. **Iniciar el frontend Vite** (en otra terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Abrir el navegador** en `http://localhost:5173`

4. **Verificar en la consola del navegador** que no hay errores de CORS

## 🔍 Solución de Problemas

### Si aún hay errores de CORS:

1. **Verificar que el backend esté corriendo** en `http://localhost:5000`
2. **Verificar logs del backend** para ver si reconoce el origen
3. **Limpiar caché del navegador** (Ctrl+Shift+R)
4. **Verificar que no hay proxy** en el frontend que interfiera

### Logs Esperados en el Backend:

```
INFO - CORS configurado con orígenes: ['http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:5173', 'http://127.0.0.1:5173']
```

## ✅ Resultado Esperado

Después de aplicar estos cambios, el dashboard de Vue debería poder:

- ✅ Conectarse al backend Flask sin errores de CORS
- ✅ Cargar datos desde `/api/sensor/todas-lecturas`
- ✅ Mostrar datos reales en lugar del modo demostración
- ✅ Funcionar tanto en puerto 8080 (Vue CLI) como 5173 (Vite)
