const int strobePin = 9;   // The GPIO pin connected to your MOSFET
int strobeHz = 3;         // How many flashes per second (try 10 to 60)
bool isStrobing = true;

void setup() {
  pinMode(strobePin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == '1') {
      isStrobing = true;
    } else if (command == '0') {
      isStrobing = false;
    }
  }

  if (isStrobing) {
    // Calculate the total cycle time in milliseconds
    // 1000ms / 20Hz = 50ms per total cycle
    int cycleTime = 1000 / strobeHz; 

    // Pulse the light
    digitalWrite(strobePin, HIGH); 
    
    // Keep the 'ON' time very short (5-10ms) for a sharp "freeze frame" effect
    // and to keep your MOSFET/Transistor cool.
    delay(5); 
    
    digitalWrite(strobePin, LOW);
    
    // The rest of the time is spent 'OFF'
    delay(cycleTime - 5); 
  } else {
    digitalWrite(strobePin, LOW);
  }
}