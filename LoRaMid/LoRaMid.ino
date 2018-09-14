#include <LoRa.h>
#define self 2
void setup() {
  // put your setup code here, to run once:
  LoRa.begin(915E6);
  LoRa.setSignalBandwidth(250e3);
  LoRa.setPreambleLength(6);
  Serial.begin(115200);
}

int children[] = {3};
char message[256];
bool waitingForResp = false;
bool waitingForInc = true;
int parent = 0;
int recv = 0;
int counter = 0;
long last = 0;

void loop() {
  if (waitingForInc || waitingForResp)
  {
    recv = LoRa.parsePacket();
    if (recv)
    {
      for (int i = 0; i < recv; i++)
      {
        message[i] = LoRa.read();
      }
      if (message[0] == 0x41 && message[1] == self)
      {
        processRequest();
        waitingForInc = false;
        waitingForResp = true;
        last = millis();
      }
      if (message[0] == 0x43)
      {
        sendMsg(parent, recv);
        waitingForInc = true;
        waitingForResp = false;
      }
    }
  }
  if (waitingForResp && millis() - last > 2000)
  {
    sendNoResponse(parent);
    
    waitingForResp = false;
    waitingForInc = true;
  }
}

void processRequest()
{
  Serial.println("Request received");
  sendRequest(children[counter]);
  waitingForResp = true;
} 

void sendRequest(int target)
{
  Serial.print("Request sent to: ");
  Serial.println(target);
  LoRa.beginPacket();
  LoRa.write(0x41);
  LoRa.write(target);
  LoRa.write(self);
  LoRa.endPacket();
  waitingForResp = true;
}

void sendMsg(int target, int msgEnd)
{
  Serial.print("Message sent to: ");
  Serial.println(target);
  LoRa.beginPacket();
  LoRa.write(0x43);
  LoRa.write(target);
  for (int i = 1; i < msgEnd; i++)
  {
    LoRa.write(message[i]);
  }
  LoRa.endPacket();
}

void sendNoResponse(int target)
{
  Serial.println("No response from child");
  LoRa.beginPacket();
  LoRa.write(0x43);
  LoRa.write(0);
  LoRa.print("No Response");
  LoRa.endPacket(); 
}

