#include <Servo.h>

Servo servo;
int delayTime;

void setup() {
  Serial.begin(9600);
  servo.attach(6);
  delayTime = 2000;
}

void loop() {
  servo.write(0);
  delay(delayTime);
  servo.write(90);
  delay(delayTime);
}
