# --- ETAPA 1: Construcción (Build) ---
# CORRECCIÓN: Se actualiza a Node.js 20 para ser compatible con la versión de Vite
FROM node:20-alpine as build-stage

# Nota: No necesitamos VITE_API_URL aquí porque la detección se hace en tiempo de ejecución
# desde el navegador del cliente

WORKDIR /app

# Copiar archivos de dependencias e instalar
# Asegurar que se instalen las devDependencies (necesarias para el build)
COPY package*.json ./
# Instalar todas las dependencias incluyendo devDependencies
# npm install por defecto instala devDependencies a menos que NODE_ENV=production
RUN npm install

# Copiar el código fuente de la aplicación (node_modules se excluye con .dockerignore)
COPY . .

# Construir la aplicación para producción
# Usar npm run build que ejecuta el script definido en package.json
RUN npm run build

# --- ETAPA 2: Servidor (Serve) ---
FROM nginx:stable-alpine as production-stage

# Copiar los archivos construidos desde la etapa anterior
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copiar configuración de Nginx para Vue Router
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer el puerto 80
EXPOSE 80

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]