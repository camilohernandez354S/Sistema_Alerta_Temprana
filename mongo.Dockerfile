FROM mongo:latest

# Crear directorio para datos
RUN mkdir -p /data/db

# Exponer puerto de MongoDB
EXPOSE 27017

# Comando para iniciar MongoDB
CMD ["mongod", "--bind_ip_all"]
