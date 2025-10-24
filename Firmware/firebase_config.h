#ifndef FIREBASE_CONFIG_H
#define FIREBASE_CONFIG_H

#include <Firebase.h>

#define DATABASE_URL "https://log--analyzer-web-default-rtdb.firebaseio.com/"
Firebase fb(DATABASE_URL);  // Sem autenticação

void sendToFirebase(float lat, float lon, float alt, float speed, float heading, const String& date) {
  // GGA
  fb.setFloat("gnss/latitude", lat);
  fb.setFloat("gnss/longitude", lon);
  fb.setFloat("gnss/altitude", alt);

  // RMC
  fb.setFloat("gnss_rmc/latitude", lat + 0.00001);
  fb.setFloat("gnss_rmc/longitude", lon + 0.00001);
  fb.setFloat("gnss_rmc/speed_kmh", speed);
  fb.setFloat("gnss_rmc/heading", heading);
  fb.setString("gnss_rmc/date", date);
}


void sendVoltage(float voltage){

fb.setFloat("agv/voltage", voltage);

}


void sendRawEntradaToFirebase(const String& entrada) {
  fb.setString("gnss/raw", entrada);
}

#endif
