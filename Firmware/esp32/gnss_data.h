#ifndef GNSS_DATA_H
#define GNSS_DATA_H

float latitude = -23.567000;
float longitude = -46.642000;
float altitude = 780.0;
float speed_kmh = 44.6;
float heading = 73.4;

float voltage = 12.0;

String entrada = "";

String gnssDate = "250625"; // ddMMyy

void updateGnssData() {
  latitude += 0.00005;
  longitude += 0.00004;
  altitude += random(-2, 3) * 0.1;
  speed_kmh += random(-10, 10) * 0.2;
  heading += random(-5, 5);
  if (heading >= 360) heading -= 360;
  if (heading < 0) heading += 360;
}

void initGnssSerial() {
  Serial2.begin(9600, SERIAL_8N1, 16, 17); // RX = GPIO16, TX = GPIO17 (pode mudar)
}



void readGnss() {
  while (Serial2.available()) {
    char c = Serial2.read();
    
    // Ignora caracteres inválidos antes do início de uma sentença
    if (entrada.length() == 0 && c != '$') continue;

    entrada += c;
    Serial.print(c);  // Mostra caractere individualmente (debug)

    // Final de linha detectado
    if (c == '\n') {
      entrada.trim(); // remove espaços e \r
      Serial.println("\n=======================");
      Serial.println("📡 Sentença GNSS recebida:");
      Serial.println(entrada);
      Serial.println("=======================\n");
      
      // Aqui você pode chamar seu parser se quiser
      // parseNMEA(entrada);

      entrada = ""; // limpa para próxima leitura
      break; // sai para processar uma sentença por vez
    }
  }
}





#endif
