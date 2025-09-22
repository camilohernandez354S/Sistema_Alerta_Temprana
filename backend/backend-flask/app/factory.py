"""
Factory básico para compatibilidad
"""

class ServiceFactory:
    """Factory básico para servicios"""
    
    def __init__(self):
        pass
    
    def cleanup(self):
        """Limpiar recursos"""
        pass

# Instancia global del factory
service_factory = ServiceFactory()
