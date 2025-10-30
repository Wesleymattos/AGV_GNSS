#include <WiFi.h>

// GPIOs para cada saída
#define PIN_CH_GERAL  2
#define PIN_DCAC      4
#define PIN_NT03_1    5
#define PIN_NT03_2    18
#define PIN_R1        19
#define PIN_R2        21
#define PIN_R3        22

void setup() {
  delay(1000); // Estabiliza o boot
  Serial.begin(115200);

  // Inicializa GPIOs como saída e deixa todos ligados (LOW)
  pinMode(PIN_CH_GERAL, OUTPUT);
  pinMode(PIN_DCAC, OUTPUT);
  pinMode(PIN_NT03_1, OUTPUT);
  pinMode(PIN_NT03_2, OUTPUT);
  pinMode(PIN_R1, OUTPUT);
  pinMode(PIN_R2, OUTPUT);
  pinMode(PIN_R3, OUTPUT);

  // Liga todas as saídas no boot
  digitalWrite(PIN_CH_GERAL, LOW);
  delay(500);
  digitalWrite(PIN_DCAC, LOW);
  delay(500);
  digitalWrite(PIN_NT03_1, LOW);
  delay(500);
  digitalWrite(PIN_NT03_2, LOW);
  delay(500);
  digitalWrite(PIN_R1, LOW);
  delay(500);
  digitalWrite(PIN_R2, LOW);
  delay(500);
  digitalWrite(PIN_R3, LOW);
  delay(500);

  Serial.println("Digite comandos para acionar saidas:");
  Serial.println("Exemplo: CH_GERAL_ON (liga), R1_OFF (desliga), etc.");
}

void loop() {
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();

    // CH_GERAL
    if (comando == "CH_GERAL_ON") {
      digitalWrite(PIN_CH_GERAL, LOW); // desliga eletricamente
      Serial.println("CH_GERAL ligado");
    } else if (comando == "CH_GERAL_OFF") {
      digitalWrite(PIN_CH_GERAL, HIGH); // liga eletricamente
      Serial.println("CH_GERAL desligado");
    }

    // DCAC
    else if (comando == "DCAC_ON") {
      digitalWrite(PIN_DCAC, LOW);
      Serial.println("DCAC ligado");
    } else if (comando == "DCAC_OFF") {
      digitalWrite(PIN_DCAC, HIGH);
      Serial.println("DCAC desligado");
    }

    // NT03_1
    else if (comando == "NT03_1_ON") {
      digitalWrite(PIN_NT03_1, LOW);
      Serial.println("NT03_1 ligado");
    } else if (comando == "NT03_1_OFF") {
      digitalWrite(PIN_NT03_1, HIGH);
      Serial.println("NT03_1 desligado");
    }

    // NT03_2
    else if (comando == "NT03_2_ON") {
      digitalWrite(PIN_NT03_2, LOW);
      Serial.println("NT03_2 ligado");
    } else if (comando == "NT03_2_OFF") {
      digitalWrite(PIN_NT03_2, HIGH);
      Serial.println("NT03_2 desligado");
    }

    // R1
    else if (comando == "R1_ON") {
      digitalWrite(PIN_R1, LOW);
      Serial.println("R1 ligado");
    } else if (comando == "R1_OFF") {
      digitalWrite(PIN_R1, HIGH);
      Serial.println("R1 desligado");
    }

    // R2
    else if (comando == "R2_ON") {
      digitalWrite(PIN_R2, LOW);
      Serial.println("R2 ligado");
    } else if (comando == "R2_OFF") {
      digitalWrite(PIN_R2, HIGH);
      Serial.println("R2 desligado");
    }

    // R3
    else if (comando == "R3_ON") {
      digitalWrite(PIN_R3, LOW);
      Serial.println("R3 ligado");
    } else if (comando == "R3_OFF") {
      digitalWrite(PIN_R3, HIGH);
      Serial.println("R3 desligado");
    }

    else {
      Serial.println("Comando invalido: " + comando);
    }
  }
}