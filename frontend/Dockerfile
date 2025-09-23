# --- ETAPA 1: Construcción (Build) ---
# CORRECCIÓN: Se actualiza a Node.js 20 para ser compatible con la versión de Vite
FROM node:20-alpine as build-stage

WORKDIR /app

# Copiar archivos de dependencias e instalar
COPY package*.json ./
RUN npm install

# Copiar el código fuente de la aplicación
COPY . .

# Construir la aplicación para producción
RUN npm run build

# --- ETAPA 2: Servidor (Serve) ---
FROM nginx:stable-alpine as production-stage

# Copiar los archivos construidos desde la etapa anterior
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Exponer el puerto 80
EXPOSE 80

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]