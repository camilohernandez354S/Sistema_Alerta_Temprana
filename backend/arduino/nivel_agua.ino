/*
 * Sistema de Alerta Temprana - Sensor de Nivel de Agua
 * 
 * Este código controla un sensor ultrasónico HC-SR04 para medir el nivel de agua
 * y clasificar el estado en: Sequía, Normal o Inundación.
 * 
 * Características:
 * - Muestreo cada 5 segundos (configurable)
 * - Clasificación automática del estado
 * - Indicadores visuales (LEDs) y sonoros (buzzer)
 * - Comunicación serial para envío de datos
 * 
 * Autor: Sistema de Alerta Temprana
 * Versión: 2.0 - Reestructurado
 */

// =============================================================================
// CONSTANTES Y CONFIGURACIÓN
// =============================================================================

// Pines de hardware
#define TRIG_PIN 3      // Pin de trigger del sensor ultrasónico
#define ECHO_PIN 4      // Pin de echo del sensor ultrasónico
#define BUZZER_PIN 12   // Pin del buzzer
#define LED_ROJO 8      // LED indicador de inundación
#define LED_AMARILLO 9  // LED indicador de nivel normal
#define LED_VERDE 10    // LED indicador de sequía

// Configuración de temporización (en milisegundos)
const unsigned long INTERVALO_MUESTREO = 5000;  // Cada 5 segundos
// NOTA: Para cambiar la frecuencia de muestreo, modifica el valor de INTERVALO_MUESTREO
// Ejemplo: 10000 = cada 10 segundos, 2000 = cada 2 segundos

// Umbrales de clasificación (en centímetros)
const float UMBRAL_INUNDACION = 15.0;  // Menos de 15cm = Inundación
const float UMBRAL_SEQUIA = 40.0;      // Más de 40cm = Sequía
// NOTA: Para ajustar los umbrales, modifica los valores de UMBRAL_INUNDACION y UMBRAL_SEQUIA
// Valores entre UMBRAL_INUNDACION y UMBRAL_SEQUIA se consideran "Normal"

// Configuración del sensor ultrasónico
const unsigned long TIMEOUT_ULTRASONICO = 30000;  // Timeout en microsegundos
const float VELOCIDAD_SONIDO = 0.034;             // cm/microsegundo

// =============================================================================
// VARIABLES GLOBALES
// =============================================================================

unsigned long ultimoTiempo = 0;  // Último tiempo de muestreo
bool sistemaInicializado = false; // Flag de inicialización

// Variables para control remoto
bool buzzerControlRemoto = false;  // Control remoto del buzzer activado
bool buzzerForzadoOff = false;     // Buzzer forzado a apagado por comando remoto
int frecuenciaRemota = 1000;       // Frecuencia configurada remotamente
String comandoBuffer = "";         // Buffer para comandos seriales

// =============================================================================
// CONFIGURACIÓN INICIAL
// =============================================================================

void setup() {
  // Inicialización de comunicación serial
  Serial.begin(9600);
  
  // Configuración de pines de entrada
  pinMode(ECHO_PIN, INPUT);
  
  // Configuración de pines de salida
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(LED_AMARILLO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  
  // Estado inicial de LEDs (apagados)
  digitalWrite(LED_ROJO, LOW);
  digitalWrite(LED_AMARILLO, LOW);
  digitalWrite(LED_VERDE, LOW);
  
  // Estado inicial del buzzer (silencioso)
  noTone(BUZZER_PIN);
  
  // Inicialización del tiempo de referencia
  ultimoTiempo = millis();
  sistemaInicializado = true;
  
  // Mensaje de inicio
  Serial.println("=== Sistema de Alerta Temprana - Sensor de Nivel de Agua ===");
  Serial.println("Sistema inicializado correctamente");
  Serial.println("Intervalo de muestreo: " + String(INTERVALO_MUESTREO) + " ms");
  Serial.println("Umbral Inundación: " + String(UMBRAL_INUNDACION) + " cm");
  Serial.println("Umbral Sequía: " + String(UMBRAL_SEQUIA) + " cm");
  Serial.println("=============================================================");
}

// =============================================================================
// BUCLE PRINCIPAL
// =============================================================================

void loop() {
  // Verificar si el sistema está inicializado
  if (!sistemaInicializado) {
    return;
  }
  
  // Procesar comandos seriales entrantes
  procesarComandosSeriales();
  
  // Verificar si es momento de tomar una nueva muestra
  if (millis() - ultimoTiempo >= INTERVALO_MUESTREO) {
    // Actualizar el tiempo de la última muestra
    ultimoTiempo = millis();
    
    // Tomar lectura del sensor
    float nivelAgua = leerNivelAgua();
    
    // Clasificar el estado del agua
    String estado = clasificarEstado(nivelAgua);
    
    // Enviar datos por comunicación serial
    enviarLectura(nivelAgua, estado);
    
    // Actualizar indicadores visuales y sonoros (solo si no hay control remoto)
    if (!buzzerControlRemoto) {
      actualizarIndicadores(estado);
    } else {
      // Solo actualizar LEDs, buzzer controlado remotamente
      actualizarLEDs(estado);
    }
  }
}

// =============================================================================
// FUNCIONES AUXILIARES
// =============================================================================

/**
 * Lee el nivel de agua usando el sensor ultrasónico HC-SR04
 * @return float - Distancia en centímetros (nivel de agua)
 */
float leerNivelAgua() {
  long duracion;
  float distancia;
  
  // Generar pulso de trigger
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Leer el eco del sensor
  duracion = pulseIn(ECHO_PIN, HIGH, TIMEOUT_ULTRASONICO);
  
  // Calcular distancia (si se recibió eco válido)
  if (duracion > 0) {
    distancia = duracion * VELOCIDAD_SONIDO / 2.0;
  } else {
    // En caso de timeout, retornar valor de error
    distancia = -1.0;
  }
  
  return distancia;
}

/**
 * Clasifica el estado del agua según los umbrales definidos
 * @param nivel - Nivel de agua en centímetros
 * @return String - Estado: "Inundación", "Normal" o "Sequía"
 */
String clasificarEstado(float nivel) {
  // Verificar si la lectura es válida
  if (nivel < 0) {
    return "Error";
  }
  
  // Clasificar según umbrales
  if (nivel <= UMBRAL_INUNDACION) {
    return "Inundación";
  } else if (nivel >= UMBRAL_SEQUIA) {
    return "Sequía";
  } else {
    return "Normal";
  }
}

/**
 * Envía la lectura por comunicación serial en formato estructurado
 * @param nivel - Nivel de agua en centímetros
 * @param estado - Estado clasificado del agua
 */
void enviarLectura(float nivel, String estado) {
  // Formato de salida: timestamp, nivel, estado
  Serial.print("TIMESTAMP:");
  Serial.print(millis());
  Serial.print(",NIVEL:");
  Serial.print(nivel, 2);
  Serial.print(",ESTADO:");
  Serial.print(estado);
  Serial.println();
  
  // TODO: Aquí se puede agregar envío de datos a servidor Flask
  // Opciones: WiFi (ESP8266/ESP32), Ethernet, o comunicación serial
  // con módulo de comunicación externo
}

/**
 * Actualiza los indicadores visuales y sonoros según el estado
 * @param estado - Estado del agua ("Inundación", "Normal", "Sequía", "Error")
 */
void actualizarIndicadores(String estado) {
  // Actualizar LEDs
  actualizarLEDs(estado);
  
  // Actualizar buzzer solo si no está forzado a apagado
  if (!buzzerForzadoOff) {
    actualizarBuzzer(estado);
  } else {
    noTone(BUZZER_PIN);
  }
}

/**
 * Actualiza solo los LEDs según el estado
 * @param estado - Estado del agua
 */
void actualizarLEDs(String estado) {
  // Apagar todos los LEDs primero
  digitalWrite(LED_ROJO, LOW);
  digitalWrite(LED_AMARILLO, LOW);
  digitalWrite(LED_VERDE, LOW);
  
  // Activar LED según el estado
  if (estado == "Inundación") {
    digitalWrite(LED_ROJO, HIGH);
  } else if (estado == "Sequía") {
    digitalWrite(LED_VERDE, HIGH);
  } else if (estado == "Normal") {
    digitalWrite(LED_AMARILLO, HIGH);
  } else {
    // Error: parpadeo rápido de LED rojo
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_ROJO, HIGH);
      delay(100);
      digitalWrite(LED_ROJO, LOW);
      delay(100);
    }
  }
}

/**
 * Actualiza el buzzer según el estado
 * @param estado - Estado del agua
 */
void actualizarBuzzer(String estado) {
  noTone(BUZZER_PIN);
  
  if (estado == "Inundación") {
    tone(BUZZER_PIN, buzzerControlRemoto ? frecuenciaRemota : 1500);
  } else if (estado == "Sequía") {
    tone(BUZZER_PIN, buzzerControlRemoto ? frecuenciaRemota : 400);
  }
}

/**
 * Procesa comandos seriales entrantes para control remoto
 */
void procesarComandosSeriales() {
  while (Serial.available()) {
    char c = Serial.read();
    
    if (c == '\n') {
      // Procesar comando completo
      procesarComando(comandoBuffer);
      comandoBuffer = "";
    } else {
      comandoBuffer += c;
    }
  }
}

/**
 * Procesa un comando específico
 * @param comando - Comando JSON recibido
 */
void procesarComando(String comando) {
  comando.trim();
  
  if (comando.length() == 0) return;
  
  // Parsing básico de JSON (simplificado)
  if (comando.indexOf("BUZZER_ON") >= 0) {
    buzzerControlRemoto = true;
    buzzerForzadoOff = false;
    
    // Extraer frecuencia si está presente
    int freqIndex = comando.indexOf("frequency");
    if (freqIndex >= 0) {
      int startIndex = comando.indexOf(":", freqIndex) + 1;
      int endIndex = comando.indexOf(",", startIndex);
      if (endIndex == -1) endIndex = comando.indexOf("}", startIndex);
      
      if (startIndex > 0 && endIndex > startIndex) {
        String freqStr = comando.substring(startIndex, endIndex);
        freqStr.trim();
        frecuenciaRemota = freqStr.toInt();
        if (frecuenciaRemota < 100) frecuenciaRemota = 1000; // Valor por defecto
      }
    }
    
    tone(BUZZER_PIN, frecuenciaRemota);
    enviarRespuesta("success", "Buzzer activado remotamente");
    
  } else if (comando.indexOf("BUZZER_OFF") >= 0) {
    buzzerControlRemoto = false;
    buzzerForzadoOff = true;
    noTone(BUZZER_PIN);
    enviarRespuesta("success", "Buzzer desactivado remotamente");
    
  } else if (comando.indexOf("STATUS") >= 0) {
    enviarEstadoDispositivo();
    
  } else if (comando.indexOf("RESET") >= 0) {
    buzzerControlRemoto = false;
    buzzerForzadoOff = false;
    frecuenciaRemota = 1000;
    noTone(BUZZER_PIN);
    enviarRespuesta("success", "Sistema reiniciado");
    
  } else {
    enviarRespuesta("error", "Comando no reconocido: " + comando);
  }
}

/**
 * Envía una respuesta JSON por serial
 * @param status - Estado de la respuesta
 * @param message - Mensaje de la respuesta
 */
void enviarRespuesta(String status, String message) {
  Serial.print("{\"status\":\"");
  Serial.print(status);
  Serial.print("\",\"message\":\"");
  Serial.print(message);
  Serial.print("\",\"timestamp\":");
  Serial.print(millis());
  Serial.println("}");
}

/**
 * Envía el estado actual del dispositivo
 */
void enviarEstadoDispositivo() {
  Serial.print("{\"status\":\"success\",\"device_status\":\"online\",");
  Serial.print("\"buzzer_control_remoto\":");
  Serial.print(buzzerControlRemoto ? "true" : "false");
  Serial.print(",\"buzzer_forzado_off\":");
  Serial.print(buzzerForzadoOff ? "true" : "false");
  Serial.print(",\"frecuencia_remota\":");
  Serial.print(frecuenciaRemota);
  Serial.print(",\"uptime\":");
  Serial.print(millis());
  Serial.print(",\"timestamp\":");
  Serial.print(millis());
  Serial.println("}");
}