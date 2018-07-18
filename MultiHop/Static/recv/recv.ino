#include <SPI.h>
#include <LoRa.h>

void setup() {
  Serial.begin(115200);
  LoRa.begin(915E6);
  pinMode(LED_BUILTIN, OUTPUT);
}

bool lit = false;
#define id 0x44
#define dest 0x55

void loop() {
  //Packet format: dest, source, data
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    byte recvDest = LoRa.read();
    byte recvSource = LoRa.read();
    byte recvData = LoRa.read();
    
//    Serial.println(recvData, HEX);
    if (recvDest == id) {
      digitalWrite(LED_BUILTIN, recvData == 0x01 ? HIGH : LOW);
      LoRa.beginPacket();
      LoRa.write(dest);
      LoRa.write(recvSource);
      LoRa.write(recvData);
      LoRa.endPacket();
    }
  }
}
