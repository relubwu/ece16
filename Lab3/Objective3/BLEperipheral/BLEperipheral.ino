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

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);


void setup() {
  Serial.begin(9600);
  BTserial.begin(9600);
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
