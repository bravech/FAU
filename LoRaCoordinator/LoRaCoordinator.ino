#include <LoRa.h>
#define self 0
void setup() {
  // put your setup code here, to run once:
  LoRa.begin(915E6);
  LoRa.setSignalBandwidth(250e3);
  LoRa.setPreambleLength(6);
  Serial.begin(115200);
}

int children[] = {1, 2};
int len = sizeof(children) / sizeof(*children);
bool waitingForResp = false;
int counter = 0;
char message[265];
int recv = 0;
long last = 2;

void loop() {
  if (!waitingForResp && millis() - last > 2000)
  {
//    Serial.println("A");
    sendRequest(children[counter]);
  }
  else
  {
    if (millis() - last > 4000)
    {
      Serial.println(">2s since last msg");
      incrementCounter();
    }
    else
    {
      recv = LoRa.parsePacket();
      if (recv)
      {
        for (int i = 0; i < recv; i++)
        {
          message[i] = LoRa.read();
        }
        if (message[0] == 0x43)
        {
          processMsg();
        }
      }
    }
  }

}

void sendRequest(int target)
{
  LoRa.beginPacket();
  LoRa.write(0x41);
  LoRa.write(target);
  LoRa.endPacket();
  Serial.print("Sending request to: ");
  Serial.println(target);
  waitingForResp = true;
}

void processMsg()
{
//  Serial.println("Message received");
  if (message[1] == self)
  {
//    Serial.println("Message addressed to self");
    Serial.print('"');
    for (int i = 2; i < recv; i++)
    {
      Serial.print(message[i]);
    }
    Serial.print('"');
    Serial.print(" received from: ");
    Serial.println(children[counter]);
    delay(100);
    waitingForResp = false;
    incrementCounter();
  }
}

bool inList(int test, int *list)
{
  for (int i = 0; i < sizeof(list) / sizeof(*list); i++)
  {
    if (list[i] == test)
    {
      return true;
    }
  }
  return false;
}

void incrementCounter()
{
//  Serial.println("Children counter incremented");
  counter++;
  counter = counter % len;
//  Serial.print("Child counter: ");
//  Serial.println(counter);
  waitingForResp = false;
  last = millis();
}

