#include <LoRa.h>
#define self 3
void setup()
{
  LoRa.begin(915E6);
  LoRa.setSignalBandwidth(250e3);
  LoRa.setPreambleLength(6);
  Serial.begin(115200);
}

char message[256];

void loop()
{
  int recv = LoRa.parsePacket();
  if (recv)
  {
    Serial.println("Packet received");
    for (int i = 0; i < recv; i++)
    {
      message[i] = LoRa.read();
    }
    if (message[0] == 0x41 && message[1] == self)
    {
      Serial.println("Request recieved to self");
      processRequest();
    }
  }
}


void processRequest()
{
  LoRa.beginPacket();
  LoRa.write(0x43);
  LoRa.print("Reading");
  LoRa.endPacket();
  Serial.print("Sending message to: ");
  Serial.println(1);
}

