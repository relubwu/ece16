/*
  Analog Input - IR

  Demonstrates analog input of IR emitter and receiver circuit
  Plots data via serial onto serial plotter

  created by David Cuartielles
  modified 30 Aug 2011
  By Tom Igoe
  modified 30 Apr 2019
  By Baichuan Wu

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/AnalogInput
*/

int sensorPin = A1;    // select the input pin for the potentiometer
int sensorValue = 0;  // variable to store the value coming from the sensor

void setup() {
  // start serial comm
  Serial.begin(9600);
  Serial.println("Serial started");
}

void loop() {
  // read the value from the sensor:
  sensorValue = analogRead(sensorPin);
  // export data via serial to plotter
  Serial.println(sensorValue);
  // delay(10);
}
