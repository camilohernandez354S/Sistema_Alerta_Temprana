# AlertsPanel Component

## Descripción
El componente `AlertsPanel.vue` es responsable de mostrar y gestionar las alertas activas del sistema de monitoreo de agua. Sigue los principios SOLID y mantiene una arquitectura modular y limpia.

## Características

### ✅ Funcionalidades Implementadas
- **Visualización de alertas**: Muestra alertas de sequía, inundación y normales
- **Colores diferenciados**: 
  - 🔴 Rojo para inundaciones
  - 🟡 Amarillo para sequías  
  - 🟢 Verde para estados normales
- **Información detallada**:
  - Tipo de alerta
  - Nivel de agua en cm
  - Estado (Activa, Resuelta, Descartada)
  - Hora de creación formateada
- **Acciones disponibles**:
  - Resolver alerta
  - Descartar alerta
  - Actualizar lista
  - Cargar más alertas
- **Actualización automática**: Cada 30 segundos
- **Diseño responsive**: Compatible con dispositivos móviles

### 🎨 Diseño
- Utiliza **Tailwind CSS** para estilos consistentes
- Iconos de **Font Awesome** para mejor UX
- Animaciones suaves y feedback visual
- Estados de carga y error manejados

## Uso

### Importación
```vue
<template>
  <AlertsPanel @alerta-procesada="manejarAlertaProcesada" />
</template>

<script>
import AlertsPanel from '@/components/dashboard/AlertsPanel.vue'

export default {
  components: {
    AlertsPanel
  },
  methods: {
    manejarAlertaProcesada(evento) {
      console.log('Alerta procesada:', evento.mensaje)
    }
  }
}
</script>
```

### Eventos Emitidos
- `alerta-procesada`: Se emite cuando una alerta es resuelta o descartada
  ```javascript
  {
    id: "alertaId",
    accion: "resolver|descartar", 
    mensaje: "Mensaje de confirmación"
  }
  ```

## Arquitectura

### Principios Aplicados
- **SRP (Single Responsibility Principle)**: El componente solo maneja la visualización de alertas
- **DRY (Don't Repeat Yourself)**: Lógica reutilizable extraída al servicio
- **KISS (Keep It Simple, Stupid)**: Interfaz simple y clara

### Estructura de Archivos
```
src/
├── components/dashboard/
│   ├── AlertsPanel.vue          # Componente principal
│   └── README_AlertsPanel.md    # Esta documentación
└── services/
    └── alertasService.js        # Servicio para manejar alertas
```

## API Endpoints Utilizados

### GET /api/sensor/alertas
Obtiene las alertas del sistema
```javascript
// Respuesta esperada
{
  "alertas": [
    {
      "_id": "alertaId",
      "nivel_agua": 45.2,
      "estado": "sequía",
      "timestamp": "2025-09-22T10:30:00Z",
      "tipo": "sequía"
    }
  ],
  "total": 1
}
```

### PUT /api/sensor/alertas/:id/resolver
Marca una alerta como resuelta

### PUT /api/sensor/alertas/:id/descartar  
Marca una alerta como descartada

## Configuración

### Variables de Entorno
El servicio usa la URL base: `http://localhost:5000/api/sensor`

### Dependencias
- Vue 3
- Tailwind CSS
- Font Awesome (para iconos)

## Personalización

### Colores de Alertas
Los colores se pueden personalizar en `alertasService.js`:
```javascript
const estilos = {
  'sequía': {
    cardClass: 'border-yellow-200 bg-yellow-50',
    textColor: 'text-yellow-700',
    // ...
  }
  // ...
}
```

### Intervalo de Actualización
Para cambiar el intervalo de actualización automática:
```javascript
// En mounted() - actualmente 30 segundos
this.interval = setInterval(() => {
  this.cargarAlertas(false)
}, 30000) // Cambiar este valor
```

## Mejoras Futuras
- [ ] Filtros por tipo de alerta
- [ ] Ordenamiento personalizable
- [ ] Exportación de alertas
- [ ] Notificaciones push
- [ ] Historial de alertas resueltas
- [ ] Métricas y estadísticas de alertas
