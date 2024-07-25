#include <TinyGPS++.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

#define BT_RX 2
#define BT_TX 3
#define GPS_RX 5
#define GPS_TX 4

SoftwareSerial btSerial(BT_RX, BT_TX);
SoftwareSerial gpsSerial(GPS_RX, GPS_TX);

TinyGPSPlus gps;

void setup() {
  Serial.begin(9600);
  btSerial.begin(57600); // set this to your bluetooth module's baud rate
  gpsSerial.begin(9600);  // Many GPS modules use 9600 baud by default
}

void loop() {
  // Read GPS data
  while (gpsSerial.available() > 0) {
    char c = gpsSerial.read();
    if (gps.encode(c)) {
      sendLocationData();
    }
  }

  // Check for GPS timeout
  if (millis() > 5000000 && gps.charsProcessed() < 10) {
    Serial.println("WARNING: No GPS data received. Check wiring.");
  }

  delay(100);  // Short delay to avoid flooding the serial output
}

void sendLocationData() {
  if (gps.location.isValid()) {
    String gpsData = String(gps.location.lat(), 6) + "," + String(gps.location.lng(), 6);
    Serial.println(gpsData);  // Print to Serial Monitor for debugging
    btSerial.println(gpsData);  // Send over Bluetooth
  }
}
