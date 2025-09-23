"""
Configuración de Gunicorn para el Sistema de Alerta Temprana
Optimizada para producción en Render
"""

import os
import multiprocessing

# Configuración básica del servidor
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Configuración de timeouts optimizada para Render
timeout = int(os.getenv('GUNICORN_TIMEOUT', '60'))
keepalive = 2
graceful_timeout = 15

# Configuración de logs
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de memoria
worker_tmp_dir = '/dev/shm'

# Configuración de SSL (si es necesario)
# keyfile = os.getenv('SSL_KEYFILE')
# certfile = os.getenv('SSL_CERTFILE')

# Configuración de preload
preload_app = True

# Configuración de hooks
def on_starting(server):
    """Hook ejecutado al iniciar el servidor"""
    server.log.info("🚀 Iniciando Sistema de Alerta Temprana...")

def on_reload(server):
    """Hook ejecutado al recargar el servidor"""
    server.log.info("🔄 Recargando Sistema de Alerta Temprana...")

def worker_int(worker):
    """Hook ejecutado cuando un worker es interrumpido"""
    worker.log.info("⚠️ Worker interrumpido: %s", worker.pid)

def pre_fork(server, worker):
    """Hook ejecutado antes de crear un worker"""
    server.log.info("👷 Creando worker: %s", worker.age)

def post_fork(server, worker):
    """Hook ejecutado después de crear un worker"""
    server.log.info("✅ Worker creado: %s", worker.pid)

def worker_abort(worker):
    """Hook ejecutado cuando un worker es abortado"""
    worker.log.info("❌ Worker abortado: %s", worker.pid)

# Configuración específica para Flask
def when_ready(server):
    """Hook ejecutado cuando el servidor está listo"""
    server.log.info("🎉 Sistema de Alerta Temprana listo para recibir conexiones")
    server.log.info(f"📊 Configuración: {workers} workers, timeout {timeout}s")

# Configuración de entorno
raw_env = [
    'FLASK_ENV=production',
    'PYTHONPATH=/app',
]

# Configuración de archivos estáticos (si es necesario)
# static_map = {
#     '/static': '/app/static'
# }
