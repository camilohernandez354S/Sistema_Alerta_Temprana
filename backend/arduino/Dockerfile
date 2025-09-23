# Usar una imagen base de Python delgada
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la carpeta
COPY . .

# Comando para ejecutar el lector serial de forma continua
CMD ["python", "leer_serial.py"]