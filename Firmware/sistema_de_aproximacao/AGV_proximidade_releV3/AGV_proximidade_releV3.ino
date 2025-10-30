#define TRIG1_PIN 2
#define ECHO1_PIN 4
#define RELE1_PIN 18

#define TRIG2_PIN 5
#define ECHO2_PIN 17
#define RELE2_PIN 19

#define BUZZER_PIN 15

volatile float distancia1 = 999;
volatile float distancia2 = 999;
volatile bool buzzerCont = false;
unsigned long buzzerStartTime = 0;

void setup() {
  Serial.begin(115200);

  pinMode(TRIG1_PIN, OUTPUT);
  pinMode(ECHO1_PIN, INPUT);
  pinMode(RELE1_PIN, OUTPUT);
  digitalWrite(RELE1_PIN, LOW);

  pinMode(TRIG2_PIN, OUTPUT);
  pinMode(ECHO2_PIN, INPUT);
  pinMode(RELE2_PIN, OUTPUT);
  digitalWrite(RELE2_PIN, LOW);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  xTaskCreatePinnedToCore(sensor1Task, "Sensor1", 2048, NULL, 2, NULL, 0);
  xTaskCreatePinnedToCore(sensor2Task, "Sensor2", 2048, NULL, 2, NULL, 1);
  xTaskCreatePinnedToCore(buzzerTask, "Buzzer", 2048, NULL, 1, NULL, 0);
}

float medirDistancia(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000); // timeout de 30ms
  if (duration == 0) return 999; // sem leitura
  return duration * 0.034 / 2;
}

void sensor1Task(void *pvParameters) {
  for (;;) {
    distancia1 = medirDistancia(TRIG1_PIN, ECHO1_PIN);
    Serial.print("Sensor 1: ");
    Serial.print(distancia1);
    Serial.println(" cm");

    if (distancia1 < 10) {
      digitalWrite(RELE1_PIN, HIGH);
      buzzerCont = true;
      buzzerStartTime = millis();
      vTaskDelay(3000 / portTICK_PERIOD_MS);
      digitalWrite(RELE1_PIN, LOW);
      buzzerCont = false;
    }

    vTaskDelay(50 / portTICK_PERIOD_MS);
  }
}

void sensor2Task(void *pvParameters) {
  for (;;) {
    distancia2 = medirDistancia(TRIG2_PIN, ECHO2_PIN);
    Serial.print("Sensor 2: ");
    Serial.print(distancia2);
    Serial.println(" cm");

    if (distancia2 < 10) {
      digitalWrite(RELE2_PIN, HIGH);
      buzzerCont = true;
      buzzerStartTime = millis();
      vTaskDelay(3000 / portTICK_PERIOD_MS);
      digitalWrite(RELE2_PIN, LOW);
      buzzerCont = false;
    }

    vTaskDelay(50 / portTICK_PERIOD_MS);
  }
}

void buzzerTask(void *pvParameters) {
  for (;;) {
    if (buzzerCont) {
      digitalWrite(BUZZER_PIN, HIGH);
    } else {
      float distancia = min(distancia1, distancia2);
      if (distancia >= 10 && distancia <= 40) {
        //int intervalo = map(distancia, 40, 10, 500, 20);
        int intervalo = map(distancia, 40, 10, 300, 20);
        digitalWrite(BUZZER_PIN, HIGH);
        vTaskDelay(intervalo / portTICK_PERIOD_MS);
        digitalWrite(BUZZER_PIN, LOW);
        vTaskDelay(intervalo / portTICK_PERIOD_MS);
      } else {
        digitalWrite(BUZZER_PIN, LOW);
        vTaskDelay(50 / portTICK_PERIOD_MS);
      }
    }
  }
}

void loop() {
  // Nada aqui
}