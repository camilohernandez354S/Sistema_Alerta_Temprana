# Usar una imagen base de Python delgada
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos e instalar dependencias
COPY arduino/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código necesario de backend-flask (necesario para arduino_client_service)
# El contexto de build es ./backend, por lo que backend-flask está en el mismo nivel
COPY backend-flask/app ./backend-flask/app

# Copiar todo el código de la carpeta arduino
COPY arduino/ .

# Comando para ejecutar el lector serial de forma continua
CMD ["python", "leer_serial.py"]