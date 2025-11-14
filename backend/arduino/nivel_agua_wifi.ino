/*
 * Sistema de Alerta Temprana - Sensor de Nivel de Agua con WiFi
 * 
 * Este código controla un sensor ultrasónico HC-SR04 para medir el nivel de agua
 * y envía los datos directamente al servidor Flask mediante WiFi.
 * 
 * Hardware requerido:
 * - ESP8266 o ESP32
 * - Sensor ultrasónico HC-SR04
 * - LEDs y buzzer (opcional)
 * 
 * Características:
 * - Conexión WiFi automática
 * - Muestreo cada 5 segundos (configurable)
 * - Clasificación automática del estado
 * - Envío de datos HTTP al servidor Flask
 * - Indicadores visuales (LEDs) y sonoros (buzzer)
 * 
 * Autor: Sistema de Alerta Temprana
 * Versión: 3.0 - Con WiFi
 */

// Incluir configuración WiFi generada automáticamente
#include "wifi_config.h"

// Para ESP8266
#ifdef ESP8266
  #include <ESP8266WiFi.h>
  #include <ESP8266HTTPClient.h>
  #include <WiFiClient.h>
  #include <WiFiClientSecure.h>
  #define LED_BUILTIN 2  // LED integrado en ESP8266
#endif

// Para ESP32
#ifdef ESP32
  #include <WiFi.h>
  #include <HTTPClient.h>
  #include <WiFiClientSecure.h>
  #define LED_BUILTIN 2  // LED integrado en ESP32
#endif

// =============================================================================
// CONSTANTES Y CONFIGURACIÓN
// =============================================================================

// Pines de hardware (ajustar según tu conexión)
#define TRIG_PIN 5      // Pin de trigger del sensor ultrasónico (GPIO5 en ESP8266)
#define ECHO_PIN 4      // Pin de echo del sensor ultrasónico (GPIO4 en ESP8266)
#define BUZZER_PIN 12   // Pin del buzzer (GPIO12)
#define LED_ROJO 14     // LED indicador de inundación (GPIO14)
#define LED_AMARILLO 13 // LED indicador de nivel normal (GPIO13)
#define LED_VERDE 15    // LED indicador de sequía (GPIO15)

// Configuración de temporización (en milisegundos)
const unsigned long INTERVALO_MUESTREO = 5000;  // Cada 5 segundos
const unsigned long INTERVALO_ENVIO = 5000;     // Enviar datos cada 5 segundos

// Umbrales de clasificación (en centímetros)
const float UMBRAL_INUNDACION = 15.0;  // Menos de 15cm = Inundación
const float UMBRAL_SEQUIA = 40.0;      // Más de 40cm = Sequía

// Configuración del sensor ultrasónico
const unsigned long TIMEOUT_ULTRASONICO = 30000;  // Timeout en microsegundos
const float VELOCIDAD_SONIDO = 0.034;             // cm/microsegundo

// =============================================================================
// VARIABLES GLOBALES
// =============================================================================

unsigned long ultimoTiempo = 0;
unsigned long ultimoEnvio = 0;
bool wifiConectado = false;
bool sistemaInicializado = false;

// Variables para control remoto
bool buzzerControlRemoto = false;
bool buzzerForzadoOff = false;
int frecuenciaRemota = 1000;

// =============================================================================
// CONFIGURACIÓN INICIAL
// =============================================================================

void setup() {
  // Inicialización de comunicación serial
  Serial.begin(115200);
  delay(1000);
  
  Serial.println();
  Serial.println("=== Sistema de Alerta Temprana - Sensor WiFi ===");
  Serial.println("Inicializando...");
  
  // Configuración de pines
  pinMode(ECHO_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(LED_AMARILLO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Estado inicial
  digitalWrite(LED_ROJO, LOW);
  digitalWrite(LED_AMARILLO, LOW);
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_BUILTIN, HIGH);  // LED integrado apagado (inverso en ESP8266)
  noTone(BUZZER_PIN);
  
  // Conectar a WiFi
  conectarWiFi();
  
  // Inicialización del tiempo de referencia
  ultimoTiempo = millis();
  ultimoEnvio = millis();
  sistemaInicializado = true;
  
  Serial.println("Sistema inicializado correctamente");
  Serial.println("================================================");
}

// =============================================================================
// BUCLE PRINCIPAL
// =============================================================================

void loop() {
  // Verificar conexión WiFi
  if (WiFi.status() != WL_CONNECTED) {
    wifiConectado = false;
    digitalWrite(LED_BUILTIN, HIGH);  // LED apagado = sin conexión
    conectarWiFi();
  } else {
    if (!wifiConectado) {
      wifiConectado = true;
      digitalWrite(LED_BUILTIN, LOW);  // LED encendido = conectado
      Serial.println("✅ WiFi conectado");
    }
  }
  
  // Verificar si es momento de tomar una nueva muestra
  if (millis() - ultimoTiempo >= INTERVALO_MUESTREO) {
    ultimoTiempo = millis();
    
    // Tomar lectura del sensor
    float nivelAgua = leerNivelAgua();
    
    // Clasificar el estado del agua
    String estado = clasificarEstado(nivelAgua);
    
    // Mostrar datos por serial
    Serial.print("Nivel: ");
    Serial.print(nivelAgua, 2);
    Serial.print(" cm - Estado: ");
    Serial.println(estado);
    
    // Actualizar indicadores visuales
    if (!buzzerControlRemoto) {
      actualizarIndicadores(estado);
    } else {
      actualizarLEDs(estado);
    }
    
    // Enviar datos al servidor si WiFi está conectado
    if (wifiConectado && (millis() - ultimoEnvio >= INTERVALO_ENVIO)) {
      ultimoEnvio = millis();
      enviarDatosAlServidor(nivelAgua, estado);
    }
  }
  
  delay(100);  // Pequeña pausa para evitar sobrecarga
}

// =============================================================================
// FUNCIONES DE CONEXIÓN WiFi
// =============================================================================

void conectarWiFi() {
  Serial.println();
  Serial.print("Conectando a WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < WIFI_MAX_RETRIES) {
    delay(WIFI_RETRY_DELAY);
    Serial.print(".");
    intentos++;
    
    // Parpadeo del LED durante conexión
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi conectado!");
    Serial.print("   IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("   Servidor: ");
    Serial.print(SERVER_HOST);
    Serial.print(":");
    Serial.println(SERVER_PORT);
    wifiConectado = true;
    digitalWrite(LED_BUILTIN, LOW);  // LED encendido
  } else {
    Serial.println();
    Serial.println("❌ Error conectando a WiFi");
    Serial.println("   Verifica SSID y contraseña en wifi_config.h");
    wifiConectado = false;
  }
}

// =============================================================================
// FUNCIONES DEL SENSOR
// =============================================================================

float leerNivelAgua() {
  long duracion;
  float distancia;
  
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  duracion = pulseIn(ECHO_PIN, HIGH, TIMEOUT_ULTRASONICO);
  
  if (duracion > 0) {
    distancia = duracion * VELOCIDAD_SONIDO / 2.0;
  } else {
    distancia = -1.0;
  }
  
  return distancia;
}

String clasificarEstado(float nivel) {
  if (nivel < 0) {
    return "Error";
  }
  
  if (nivel <= UMBRAL_INUNDACION) {
    return "Inundación";
  } else if (nivel >= UMBRAL_SEQUIA) {
    return "Sequía";
  } else {
    return "Normal";
  }
}

// =============================================================================
// FUNCIONES DE ENVÍO DE DATOS
// =============================================================================

void enviarDatosAlServidor(float nivel, String estado) {
  if (!wifiConectado) {
    return;
  }
  
  // Construir URL del endpoint
  String protocolo = String(SERVER_PROTOCOL) + "://";
  String url = protocolo + String(SERVER_HOST);
  
  // Agregar puerto solo si no es el puerto estándar (80 para HTTP, 443 para HTTPS)
  if (USE_HTTPS && SERVER_PORT != 443) {
    url += ":" + String(SERVER_PORT);
  } else if (!USE_HTTPS && SERVER_PORT != 80) {
    url += ":" + String(SERVER_PORT);
  }
  
  // Agregar path si existe
  if (strlen(SERVER_PATH) > 0) {
    url += String(SERVER_PATH);
  }
  
  url += "/api/mediciones";
  
  // Construir JSON con los datos
  String jsonData = "{";
  jsonData += "\"NIVEL\":" + String(nivel, 2);
  jsonData += ",\"TIMESTAMP\":" + String(millis());
  jsonData += ",\"ESTADO\":\"" + estado + "\"";
  jsonData += "}";
  
  Serial.print("Enviando datos a: ");
  Serial.println(url);
  Serial.print("Datos: ");
  Serial.println(jsonData);
  
  #ifdef ESP8266
    HTTPClient http;
    if (USE_HTTPS) {
      WiFiClientSecure client;
      // Para producción, puedes deshabilitar verificación de certificado (no recomendado para producción real)
      client.setInsecure(); // Solo para desarrollo/testing
      http.begin(client, url);
    } else {
      WiFiClient client;
      http.begin(client, url);
    }
  #endif
  
  #ifdef ESP32
    HTTPClient http;
    if (USE_HTTPS) {
      WiFiClientSecure client;
      // Para producción, puedes deshabilitar verificación de certificado (no recomendado para producción real)
      client.setInsecure(); // Solo para desarrollo/testing
      http.begin(client, url);
    } else {
      http.begin(url);
    }
  #endif
  
  http.addHeader("Content-Type", "application/json");
  
  int httpResponseCode = http.POST(jsonData);
  
  if (httpResponseCode > 0) {
    Serial.print("✅ Respuesta del servidor: ");
    Serial.println(httpResponseCode);
    
    if (httpResponseCode == 201 || httpResponseCode == 200) {
      String respuesta = http.getString();
      Serial.print("   Respuesta: ");
      Serial.println(respuesta);
    }
  } else {
    Serial.print("❌ Error enviando datos: ");
    Serial.println(httpResponseCode);
    #ifdef ESP8266
      Serial.print("   Error: ");
      Serial.println(http.errorToString(httpResponseCode));
    #endif
    #ifdef ESP32
      Serial.print("   Error: ");
      Serial.println(http.errorToString(httpResponseCode));
    #endif
  }
  
  http.end();
}

// =============================================================================
// FUNCIONES DE INDICADORES
// =============================================================================

void actualizarIndicadores(String estado) {
  actualizarLEDs(estado);
  
  if (!buzzerForzadoOff) {
    actualizarBuzzer(estado);
  } else {
    noTone(BUZZER_PIN);
  }
}

void actualizarLEDs(String estado) {
  digitalWrite(LED_ROJO, LOW);
  digitalWrite(LED_AMARILLO, LOW);
  digitalWrite(LED_VERDE, LOW);
  
  if (estado == "Inundación") {
    digitalWrite(LED_ROJO, HIGH);
  } else if (estado == "Sequía") {
    digitalWrite(LED_VERDE, HIGH);
  } else if (estado == "Normal") {
    digitalWrite(LED_AMARILLO, HIGH);
  } else {
    // Error: parpadeo rápido
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_ROJO, HIGH);
      delay(100);
      digitalWrite(LED_ROJO, LOW);
      delay(100);
    }
  }
}

void actualizarBuzzer(String estado) {
  noTone(BUZZER_PIN);
  
  if (estado == "Inundación") {
    tone(BUZZER_PIN, buzzerControlRemoto ? frecuenciaRemota : 1500);
  } else if (estado == "Sequía") {
    tone(BUZZER_PIN, buzzerControlRemoto ? frecuenciaRemota : 400);
  }
}

