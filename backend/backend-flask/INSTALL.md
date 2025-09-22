# 🚀 Guía de Instalación - Backend Flask

## ⚠️ Solución para Error de BSON

Si ves el error `ImportError: cannot import name '_get_object_size' from 'bson'`, sigue estos pasos:

### 🔧 **Solución Rápida (Windows)**

1. **Ejecuta el script de setup automático:**
   ```cmd
   setup.bat
   ```

### 🔧 **Solución Manual**

1. **Desinstala el paquete bson conflictivo:**
   ```cmd
   pip uninstall bson -y
   pip uninstall pymongo -y
   ```

2. **Reinstala pymongo (que incluye bson correcto):**
   ```cmd
   pip install pymongo==4.6.1
   ```

3. **Instala el resto de dependencias:**
   ```cmd
   pip install -r requirements-clean.txt
   ```

4. **Configura el entorno:**
   ```cmd
   copy env.example .env
   mkdir logs
   ```

### 🎯 **Verificación**

1. **Prueba que funciona:**
   ```cmd
   python -c "from pymongo import MongoClient; print('✅ MongoDB import OK')"
   ```

2. **Ejecuta la aplicación:**
   ```cmd
   python run.py
   ```

## 📋 **Instalación Completa desde Cero**

### **Paso 1: Entorno Virtual (Recomendado)**
```cmd
python -m venv venv
venv\Scripts\activate
```

### **Paso 2: Configuración Automática**
```cmd
setup.bat
```

### **Paso 3: Configurar Variables de Entorno**
1. Edita el archivo `.env` con tus configuraciones
2. Especialmente `MONGO_URI` si usas MongoDB remoto

### **Paso 4: Ejecutar**
```cmd
python run.py
```

## 🧪 **Testing**

```cmd
# Tests básicos
pytest

# Tests con cobertura
pytest --cov=app --cov-report=html
```

## 🛠️ **Comandos de Desarrollo**

```cmd
# Formatear código
black app/
isort app/

# Verificar código
flake8 app/

# Limpiar archivos temporales
dev.bat clean
```

## 🐛 **Problemas Comunes**

### **Error: ModuleNotFoundError**
- Asegúrate de tener el entorno virtual activado
- Reinstala las dependencias: `pip install -r requirements-clean.txt`

### **Error de conexión MongoDB**
- Verifica que MongoDB esté ejecutándose
- Revisa la configuración en `.env`

### **Error de puertos**
- Cambia `FLASK_PORT` en `.env` si el puerto 5000 está ocupado

## 📞 **Soporte**

Si sigues teniendo problemas:
1. Verifica la versión de Python: `python --version` (requiere 3.9+)
2. Actualiza pip: `python -m pip install --upgrade pip`
3. Reinstala todo desde cero siguiendo esta guía
