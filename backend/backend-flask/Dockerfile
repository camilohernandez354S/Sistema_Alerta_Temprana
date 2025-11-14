# Etapa 1: Base de Python
# Usar una imagen oficial de Python slim
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (si fueran necesarias, ej: build-essential)
# RUN apt-get update && apt-get install -y build-essential

# Instalar pipenv (si se usa) o solo copiar requirements
# En este caso, usaremos requirements.txt
COPY requirements.txt .

# Instalar dependencias de Python
# Usar --no-cache-dir para reducir el tamaño de la imagen
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto que Gunicorn usará (definido en docker-compose)
# Docker-compose mapeará 5000 del host a este puerto
EXPOSE 5000

# Comando para iniciar la aplicación
# Usar Gunicorn para producción
# Nota: wsgi.py define 'application', no 'app'
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:application"]