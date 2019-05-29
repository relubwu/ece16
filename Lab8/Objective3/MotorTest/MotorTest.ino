/*
  MotorTest
  
  modified 29 May 2019
  By Baichuan Wu
  
*/

int motorPin = 3;    // select the input pin for the potentiometer
unsigned long startTime;
unsigned long endTime;
boolean motorState;
unsigned int gap;

void setup() {
  // initialize the digital pin as an output.
  pinMode(motorPin, OUTPUT); 
  // start serial comm
  Serial.begin(9600);
  Serial.println("Serial started");
  startTime = millis();
  motorState = false;
  gap = 1000;
}

void loop() {
  endTime = millis();
  if (endTime - startTime >= gap) {
    startTime = millis();
    if (!motorState) {
      digitalWrite(motorPin, LOW);
      motorState = true;
      gap = 200;
    } else {
      digitalWrite(motorPin, HIGH);
      motorState = false;
      gap = 1000;
    }
    Serial.println(motorState);
  }
}
