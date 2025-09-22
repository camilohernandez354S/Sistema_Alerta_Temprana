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
    
    // Actualizar indicadores visuales y sonoros
    actualizarIndicadores(estado);
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
  // Apagar todos los LEDs y el buzzer primero
  digitalWrite(LED_ROJO, LOW);
  digitalWrite(LED_AMARILLO, LOW);
  digitalWrite(LED_VERDE, LOW);
  noTone(BUZZER_PIN);
  
  // Activar indicadores según el estado
  if (estado == "Inundación") {
    // Inundación: LED rojo y tono agudo
    digitalWrite(LED_ROJO, HIGH);
    tone(BUZZER_PIN, 1500);
  } else if (estado == "Sequía") {
    // Sequía: LED verde y tono grave
    digitalWrite(LED_VERDE, HIGH);
    tone(BUZZER_PIN, 400);
  } else if (estado == "Normal") {
    // Normal: LED amarillo, sin sonido
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