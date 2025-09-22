# Usar una imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto que usa la aplicación
EXPOSE 5000

# CORRECCIÓN FINAL Y DEFINITIVA: Apuntar al objeto 'app' en el archivo 'run.py'
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]