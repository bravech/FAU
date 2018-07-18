#include <SPI.h>
#include <LoRa.h>

void setup() {
  Serial.begin(115200);
  LoRa.begin(915E6);
  pinMode(LED_BUILTIN, OUTPUT);
}

bool lit = false;
#define id 0x11
#define dest 0x22

void loop() {
  digitalWrite(LED_BUILTIN, lit ? HIGH : LOW);
  LoRa.beginPacket();
  //Packet format: dest, source, data
  LoRa.write(dest);
  LoRa.write(id);
  LoRa.write(lit);
  LoRa.endPacket();
  delay(1000);
  lit = !lit;
}
