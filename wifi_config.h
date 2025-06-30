#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#include <WiFi.h>

#define WIFI_SSID "Amigo FAMILIA OLIVEIRA"
#define WIFI_PASSWORD "27028028"

void connectToWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println("\nWi-Fi conectado! IP: " + WiFi.localIP().toString());
}

#endif
