/*
  Blink

  Turns an LED on for one second, then off for one second, repeatedly.

  Most Arduinos have an on-board LED you can control. On the UNO, MEGA and ZERO
  it is attached to digital pin 13, on MKR1000 on pin 6. LED_BUILTIN is set to
  the correct LED pin independent of which board is used.
  If you want to know what pin the on-board LED is connected to on your Arduino
  model, check the Technical Specs of your board at:
  https://www.arduino.cc/en/Main/Products

  modified 8 May 2014
  by Scott Fitzgerald
  modified 2 Sep 2016
  by Arturo Guadalupi
  modified 8 Sep 2016
  by Colby Newman
  modified 4 Apr 2019
  by Baichuan Wu

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/Blink
*/

/*
  FIELD
*/
const int onDurationSlow = 1500;
const int onDurationFast = 200;
const int defaultOnDuration = onDurationSlow;
const int defaultOffDuration = 500;
int onDuration = defaultOnDuration;
int offDuration = defaultOffDuration;
int counter;

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  // initialize serial output
  Serial.begin(9600);
}

// the loop function runs over and over again forever
void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil("\n");  // read streamed input until carriage return
    if (command.equals("SLOW\n")) {
      onDuration = onDurationSlow;  // set duration to slow (1500ms)
    }
    if (command.equals("FAST\n")) {
      onDuration = onDurationFast;  // set duration to fast (200ms)
    }
  }
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  Serial.print(++counter);           // print counter each time it's incremented
  delay(onDuration);                       // wait for defined on duration
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(offDuration);                       // wait for defined off duration
}
