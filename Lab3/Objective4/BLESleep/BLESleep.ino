/*
 * BLE connection to laptop
 * ECE16 SP19 
 * Lab2
 *
 * modified 22 Apr 2019
 *  by Baichuan Wu
 */

#include <SPI.h>
#include <Wire.h>
#include <AltSoftSerial.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

/*
 * Field
 */
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels
AltSoftSerial BTserial;
char c = ' ';
boolean NL = true;
boolean connected = false;
unsigned long throttle; // throttle
unsigned long throttleAsterik;
boolean state = true;  // BLE state ? 0 off : 1 on

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);


void setup() {
  Serial.begin(9600);
  BTserial.begin(9600);
  pinMode(4, INPUT_PULLUP); // initialize pin
  Serial.println("BTserial started");
  throttleAsterik = millis();
  
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x32
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  // Show initial display buffer contents on the screen --
  // the library initializes this with an Adafruit splash screen.
  display.display();
  delay(2000); // Pause for 2 seconds

  // Clear the buffer
  display.clearDisplay();

  // Set Styling
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.cp437(true);
}

void loop() {
  // Read from the Bluetooth module and send to the Arduino Serial Monitor
  if (BTserial.available()) {
      c = BTserial.read();
      Serial.write(c);
      if (c == 'C') {
        connected = true;
        showMessage('Connected');
      } else {
        showMessage(c);
      }
      throttle = millis();
  }
  if (connected)
    if (millis() - throttleAsterik > 1000) {
      BTserial.write('*');
      throttleAsterik = millis();
    }
  int value = digitalRead(4); // acuqire pin value
  if (checkButton(value)) {
    if (!state) {       // from off to on
      Serial.println("Start");
      BTserial.write("eNptkc1qwzAQhO+FvsOQS16gL+C4NClNmkIcQo8re22LKCujH4LfvpLTQg+6LjOz384ONmCO6Ommjabnpy25GatmZDSOxPfsULvoR3YrbLUx7CfNf7Ka4jAGVDi1LipYSZIwRlWQ5sStYwq4kDE49qhPBdlGh3Zkj1cr64APsXdUysaAw4yLFkY1TSUbJwRy3OG9x7eNa8c4S8etycOCIWlc4qGOcRRkuDctZNKOBHegK+cU7OxNt7ojU0ioxIbUCr4MK/wWoWXhZFXe+EjPrDbxbeacz3frrngpGFLSjvzYkDK8IPllV+pG+zwrnXUWY6nTMmSOz6WvsFz3eNA+Tf65fgDy5ahO");
      delay(100);
      BTserial.write("AT+ADTY0");
      delay(100);
      BTserial.write("AT+RESET");
      delay(100);
    } else {            // from on to off
      Serial.println("Sleep");
      delay(100);
      BTserial.write("AT");
      delay(100);
      BTserial.write("AT+ADTY3");
      delay(100);
      BTserial.write("AT+SLEEP");
    }
    state = !state;     // toggle state
    delay(500);
  }
}

/*
 * Covert Serial String input and pipe to Display
 * 
 * @param messageChar
 */
void showMessage(char c) {
  if (millis() - throttle > 500) {
    display.clearDisplay(); // purge previous screen
    display.setCursor(0, 0); // reset cursor position
  }
  display.write(c);
  display.display(); // execute render
}

/**
 * Check Button Status
 * @param int value
 * @return boolean result
 */
boolean checkButton(int value) {
  return (value == 0) ? true : false;
}
