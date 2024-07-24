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

unsigned long lastDebugTime = 0;
const unsigned long debugInterval = 5000; // Debug output every 5 seconds

void setup() {
  Serial.begin(9600);
  btSerial.begin(57600);
  gpsSerial.begin(9600);  // Many GPS modules use 9600 baud by default

  sendDebug("GPS and Bluetooth Debug");
  sendDebug("----------------------");
}

void loop() {
  // Read GPS data
  while (gpsSerial.available() > 0) {
    char c = gpsSerial.read();
    if (gps.encode(c)) {
      displayInfo();
    }
  }

  // Check for GPS timeout
  if (millis() > 5000000 && gps.charsProcessed() < 10) {
    sendDebug("WARNING: No GPS data received. Check wiring.");
  }

  // Check for incoming Bluetooth data
  while (btSerial.available()) {
    char received = btSerial.read();
    String msg = "Bluetooth Received: " + String(received);
    sendDebug(msg);
    
    // You can add commands here to control GPS functionality
  }

  // Periodic debug output
  if (millis() - lastDebugTime > debugInterval) {
    lastDebugTime = millis();
    sendDebug("\n--- Debug Info ---");
    sendDebug("GPS chars processed: " + String(gps.charsProcessed()));
    sendDebug("Satellites in view: " + String(gps.satellites.value()));
    sendDebug("HDOP: " + String(gps.hdop.value()));
    sendDebug("------------------\n");
  }

  delay(100);  // Short delay to avoid flooding the serial output
}

void displayInfo() {
  sendDebug("GPS Data:");
  if (gps.location.isValid()) {
    String gpsData = "Lat: " + String(gps.location.lat(), 6) + 
                     " Lon: " + String(gps.location.lng(), 6) +
                     " Alt: " + String(gps.altitude.meters());
    
    sendDebug(gpsData);
    btSerial.print(gpsData);  // Send valid GPS data over Bluetooth
  } else {
    sendDebug("Location: Not Available");
  }

  String dateTime = "Date/Time: ";
  if (gps.date.isValid() && gps.time.isValid()) {
    dateTime += String(gps.date.year()) + "/" +
                String(gps.date.month()) + "/" +
                String(gps.date.day()) + " " +
                String(gps.time.hour()) + ":" +
                String(gps.time.minute()) + ":" +
                String(gps.time.second());
    btSerial.print(dateTime);  // Send valid Date/Time over Bluetooth
  } else {
    dateTime += "Not Available";
  }
  sendDebug(dateTime);

  sendDebug("");
}

void sendDebug(String message) {
  Serial.println(message);  // Print to Serial Monitor
  btSerial.println(message);  // Send over Bluetooth
}
