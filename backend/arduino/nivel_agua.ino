#define TRIG_PIN 3
#define ECHO_PIN 4
#define BUZZER_PIN 12
#define LED_ROJO 8
#define LED_AMARILLO 9
#define LED_VERDE 10

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(LED_AMARILLO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
}

void loop() {
  long duration;
  float distance;

  // Pulso ultrasónico
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;

  Serial.print("nivel_agua: ");
  Serial.print(distance);
  Serial.println(" cm");

  if (distance < 15) {
    // Distancia corta: LED rojo y tono agudo
    digitalWrite(LED_ROJO, HIGH);
    digitalWrite(LED_AMARILLO, LOW);
    digitalWrite(LED_VERDE, LOW);
    tone(BUZZER_PIN, 1500);
  }
  else if (distance > 40) {
    // Distancia lejana: LED verde y tono grave
    digitalWrite(LED_ROJO, LOW);
    digitalWrite(LED_AMARILLO, LOW);
    digitalWrite(LED_VERDE, HIGH);
    tone(BUZZER_PIN, 400);
  }
  else {
    // Zona intermedia: LED amarillo, sin sonido
    digitalWrite(LED_ROJO, LOW);
    digitalWrite(LED_AMARILLO, HIGH);
    digitalWrite(LED_VERDE, LOW);
    noTone(BUZZER_PIN);
  }

  delay(500);
}