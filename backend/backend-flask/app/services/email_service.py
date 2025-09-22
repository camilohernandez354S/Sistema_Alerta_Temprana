"""
Servicio para envío de emails y notificaciones
"""
from flask import current_app
from flask_mail import Mail, Message
from typing import List, Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import logging

class EmailService:
    """Servicio para manejo de emails"""
    
    def __init__(self):
        """Inicializar servicio de email"""
        self.mail = None
        self.smtp_server = None
        self.smtp_port = None
        self.smtp_username = None
        self.smtp_password = None
        self.from_email = None
        self.from_name = None
        self.templates_dir = None
        self.logger = None
    
    def init_app(self, app):
        """Inicializar Flask-Mail con la aplicación"""
        # Configurar el logger
        self.logger = app.logger
        self.logger.info("EmailService inicializado")
        
        try:
            # Configurar Flask-Mail
            app.config['MAIL_SERVER'] = app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            app.config['MAIL_PORT'] = app.config.get('MAIL_PORT', 587)
            app.config['MAIL_USE_TLS'] = app.config.get('MAIL_USE_TLS', True)
            app.config['MAIL_USERNAME'] = app.config.get('MAIL_USERNAME')
            app.config['MAIL_PASSWORD'] = app.config.get('MAIL_PASSWORD')
            app.config['MAIL_DEFAULT_SENDER'] = app.config.get('MAIL_DEFAULT_SENDER')
            
            self.mail = Mail(app)
            
            # Configurar parámetros SMTP
            self.smtp_server = app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            self.smtp_port = app.config.get('MAIL_PORT', 587)
            self.smtp_username = app.config.get('MAIL_USERNAME')
            self.smtp_password = app.config.get('MAIL_PASSWORD')
            self.from_email = app.config.get('MAIL_DEFAULT_SENDER', self.smtp_username)
            self.from_name = app.config.get('MAIL_FROM_NAME', 'Sistema de Monitoreo')
            
            # Directorio de plantillas
            self.templates_dir = os.path.join(app.root_path, 'templates', 'email')
            
            self.logger.info("✅ EmailService configurado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error configurando EmailService: {e}")
            self.mail = None
    
    def send_email(self, to_emails: List[str], subject: str, body: str, 
                   html_body: Optional[str] = None, attachments: Optional[List[Dict]] = None) -> bool:
        """
        Enviar email usando Flask-Mail
        
        Args:
            to_emails: Lista de emails destino
            subject: Asunto del email
            body: Cuerpo del email en texto plano
            html_body: Cuerpo del email en HTML (opcional)
            attachments: Lista de archivos adjuntos (opcional)
            
        Returns:
            bool: True si se envió correctamente
        """
        if not self.mail:
            if self.logger:
                self.logger.warning("EmailService no configurado")
            return False
        
        try:
            msg = Message(
                subject=subject,
                recipients=to_emails,
                body=body,
                html=html_body,
                sender=self.from_email
            )
            
            # Agregar archivos adjuntos si existen
            if attachments:
                for attachment in attachments:
                    if attachment.get('filename') and attachment.get('data'):
                        msg.attach(
                            filename=attachment['filename'],
                            content_type=attachment.get('content_type', 'application/octet-stream'),
                            data=attachment['data']
                        )
            
            self.mail.send(msg)
            if self.logger:
                self.logger.info(f"✅ Email enviado a {len(to_emails)} destinatario(s)")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error enviando email: {e}")
            return False
    
    def send_notification_email(self, user_email: str, notification_type: str, 
                               data: Dict[str, Any]) -> bool:
        """
        Enviar email de notificación
        
        Args:
            user_email: Email del usuario
            notification_type: Tipo de notificación
            data: Datos de la notificación
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            if notification_type == 'sensor_alert':
                return self._send_sensor_alert_email(user_email, data)
            elif notification_type == 'system_maintenance':
                return self._send_maintenance_email(user_email, data)
            elif notification_type == 'user_welcome':
                return self._send_welcome_email(user_email, data)
            elif notification_type == 'password_reset':
                return self._send_password_reset_email(user_email, data)
            else:
                if self.logger:
                    self.logger.warning(f"Tipo de notificación no reconocido: {notification_type}")
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error enviando email de notificación: {e}")
            return False
    
    def _send_sensor_alert_email(self, user_email: str, data: Dict[str, Any]) -> bool:
        """Enviar email de alerta de sensor"""
        sensor_data = data.get('sensor_data', {})
        alert_type = data.get('alert_type', 'unknown')
        
        # Determinar el nivel de alerta y colores
        if alert_type == 'inundation':
            alert_color = '#dc3545'  # Rojo
            alert_icon = '⚠️'
            alert_title = 'ALERTA DE INUNDACIÓN'
        elif alert_type == 'drought':
            alert_color = '#fd7e14'  # Naranja
            alert_icon = '🌵'
            alert_title = 'ALERTA DE SEQUÍA'
        else:
            alert_color = '#6c757d'  # Gris
            alert_icon = 'ℹ️'
            alert_title = 'NOTIFICACIÓN DEL SENSOR'
        
        subject = f"{alert_title} - Sistema de Monitoreo"
        
        # Cuerpo en texto plano
        body = f"""
{alert_title}

{alert_icon} Se ha detectado una condición anormal en el sistema de monitoreo de nivel de agua.

Detalles:
- Nivel de agua: {sensor_data.get('nivel_agua', 'N/A')} cm
- Estado: {sensor_data.get('estado', 'N/A')}
- Ubicación: {sensor_data.get('location', 'N/A')}
- Timestamp: {sensor_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

Por favor, verifique el sistema y tome las medidas necesarias.

---
Sistema de Monitoreo de Nivel de Agua
Este es un mensaje automático, por favor no responder.
        """
        
        # Cuerpo en HTML
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{alert_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background-color: {alert_color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .alert-details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .detail-row {{ display: flex; justify-content: space-between; margin: 8px 0; }}
        .detail-label {{ font-weight: bold; color: #495057; }}
        .detail-value {{ color: #6c757d; }}
        .footer {{ background-color: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{alert_icon} {alert_title}</h1>
        </div>
        <div class="content">
            <p>Se ha detectado una condición anormal en el sistema de monitoreo de nivel de agua.</p>
            
            <div class="alert-details">
                <div class="detail-row">
                    <span class="detail-label">Nivel de agua:</span>
                    <span class="detail-value">{sensor_data.get('nivel_agua', 'N/A')} cm</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Estado:</span>
                    <span class="detail-value">{sensor_data.get('estado', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Ubicación:</span>
                    <span class="detail-value">{sensor_data.get('location', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Timestamp:</span>
                    <span class="detail-value">{sensor_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</span>
                </div>
            </div>
            
            <p><strong>Por favor, verifique el sistema y tome las medidas necesarias.</strong></p>
        </div>
        <div class="footer">
            Sistema de Monitoreo de Nivel de Agua<br>
            Este es un mensaje automático, por favor no responder.
        </div>
    </div>
</body>
</html>
        """
        
        return self.send_email([user_email], subject, body, html_body)
    
    def _send_maintenance_email(self, user_email: str, data: Dict[str, Any]) -> bool:
        """Enviar email de mantenimiento del sistema"""
        subject = "Mantenimiento Programado - Sistema de Monitoreo"
        
        body = f"""
MANTENIMIENTO PROGRAMADO

Se ha programado un mantenimiento del sistema de monitoreo de nivel de agua.

Detalles del mantenimiento:
- Fecha: {data.get('date', 'N/A')}
- Hora: {data.get('time', 'N/A')}
- Duración estimada: {data.get('duration', 'N/A')}
- Descripción: {data.get('description', 'Mantenimiento de rutina')}

Durante el período de mantenimiento, el sistema puede no estar disponible.

---
Sistema de Monitoreo de Nivel de Agua
        """
        
        return self.send_email([user_email], subject, body)
    
    def _send_welcome_email(self, user_email: str, data: Dict[str, Any]) -> bool:
        """Enviar email de bienvenida"""
        user_name = data.get('user_name', 'Usuario')
        user_role = data.get('user_role', 'user')
        
        subject = f"Bienvenido al Sistema de Monitoreo - {user_name}"
        
        body = f"""
¡BIENVENIDO AL SISTEMA DE MONITOREO!

Hola {user_name},

Tu cuenta ha sido creada exitosamente en el Sistema de Monitoreo de Nivel de Agua.

Detalles de tu cuenta:
- Usuario: {data.get('username', 'N/A')}
- Rol: {user_role}
- Email: {user_email}

Puedes acceder al sistema en: {data.get('system_url', 'http://localhost:8080')}

¡Gracias por usar nuestro sistema!

---
Sistema de Monitoreo de Nivel de Agua
        """
        
        return self.send_email([user_email], subject, body)
    
    def _send_password_reset_email(self, user_email: str, data: Dict[str, Any]) -> bool:
        """Enviar email de recuperación de contraseña"""
        reset_token = data.get('reset_token', '')
        user_name = data.get('user_name', 'Usuario')
        reset_url = data.get('reset_url', f'http://localhost:8080/reset-password?token={reset_token}')
        expires_in = data.get('expires_in', '1 hora')
        
        subject = "Recuperación de Contraseña - Sistema de Monitoreo"
        
        # Cuerpo en texto plano
        body = f"""
RECUPERACIÓN DE CONTRASEÑA

Hola {user_name},

Has solicitado recuperar tu contraseña para el Sistema de Monitoreo de Nivel de Agua.

Para restablecer tu contraseña, haz clic en el siguiente enlace:
{reset_url}

Este enlace expirará en {expires_in}.

Si no solicitaste este cambio, puedes ignorar este email.

---
Sistema de Monitoreo de Nivel de Agua
        """
        
        # Cuerpo en HTML
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Recuperación de Contraseña</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .reset-button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .reset-button:hover {{ background-color: #0056b3; }}
        .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .footer {{ background-color: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Recuperación de Contraseña</h1>
        </div>
        <div class="content">
            <p>Hola <strong>{user_name}</strong>,</p>
            
            <p>Has solicitado recuperar tu contraseña para el Sistema de Monitoreo de Nivel de Agua.</p>
            
            <p>Para restablecer tu contraseña, haz clic en el siguiente botón:</p>
            
            <div style="text-align: center;">
                <a href="{reset_url}" class="reset-button">Restablecer Contraseña</a>
            </div>
            
            <div class="warning">
                <strong>⚠️ Importante:</strong> Este enlace expirará en {expires_in}.
            </div>
            
            <p>Si no solicitaste este cambio, puedes ignorar este email.</p>
        </div>
        <div class="footer">
            Sistema de Monitoreo de Nivel de Agua<br>
            Este es un mensaje automático, por favor no responder.
        </div>
    </div>
</body>
</html>
        """
        
        return self.send_email([user_email], subject, body, html_body)
    
    def send_bulk_notification(self, user_emails: List[str], notification_type: str, 
                              data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enviar notificación masiva a múltiples usuarios
        
        Args:
            user_emails: Lista de emails destino
            notification_type: Tipo de notificación
            data: Datos de la notificación
            
        Returns:
            Dict con estadísticas del envío
        """
        results = {
            'total': len(user_emails),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for email in user_emails:
            try:
                success = self.send_notification_email(email, notification_type, data)
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Error enviando a {email}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error enviando a {email}: {str(e)}")
        
        if self.logger:
            self.logger.info(f"Notificación masiva enviada: {results['success']}/{results['total']} exitosos")
        return results
    
    def test_connection(self) -> bool:
        """
        Probar conexión SMTP
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
                if self.logger:
                    self.logger.warning("Configuración SMTP incompleta")
                return False
            
            # Probar conexión SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.quit()
            
            if self.logger:
                self.logger.info("✅ Conexión SMTP exitosa")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error probando conexión SMTP: {e}")
            return False

# Instancia global del servicio de email
email_service = EmailService()
