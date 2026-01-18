#include <Servo.h>

Servo servo;
int delayTime;

void setup() {
  Serial.begin(9600);
  servo.attach(6);
  delayTime = 2000;
  servo.write(0);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readString();
    command.trim();
    
    if (command == "WIPE") {
      for (int i = 0; i < 2; i++) {
        servo.write(90);
        delay(delayTime/2);
        servo.write(0);
        delay(delayTime);
      }
      Serial.println("WIPED");
    }
  }
}
