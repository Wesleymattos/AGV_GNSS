//envia o nemea junto

#include "wifi_config.h"
#include "firebase_config.h"
#include "gnss_data.h"

unsigned long lastSend = 0;
const unsigned long interval = 1000;

void setup() {
  Serial.begin(115200);
  connectToWiFi();
  initGnssSerial();
}

void loop() {
  readGnss();  // Atualiza a variável entrada
  if (millis() - lastSend >= interval) {
    lastSend = millis();
    updateGnssData();
    sendToFirebase(latitude, longitude, altitude, speed_kmh, heading, gnssDate);
    sendVoltage(voltage);
    sendRawEntradaToFirebase(entrada);
    //entrada = ""; // limpa após envio

Serial.printf("ENVIADO → voltage %.1f\n",
                  voltage);
    Serial.printf("ENVIADO → Lat: %.6f, Lon: %.6f, Alt: %.1f, V: %.1f, Dir: %.1f\n",
                  latitude, longitude, altitude, speed_kmh, heading);
  }
}
