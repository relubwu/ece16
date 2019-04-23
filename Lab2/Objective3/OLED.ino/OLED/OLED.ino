/*
 * This is a demonstration of showing messages on OLED display
 * ECE16 SP19 
 * Lab2
 *
 * modified 11 Apr 2019
 *  by Baichuan Wu
 */

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

/*
 * Field
 */

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  Serial.begin(9600);

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
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil("\n");  // read streamed input until carriage return
    showMessage(message); // invoke show message
    delay(2000); // tick
  }
}

/*
 * Covert Serial String input and pipe to Display
 * 
 * @param messageString - intended message
 */
void showMessage(String messageString) {
  int messageLength = messageString.length(); // acquire char[] length
  char messageCharArray[messageLength + 1]; // instantiate char[]
  strcpy(messageCharArray, messageString.c_str()); // link char[] to corresponding String
  display.clearDisplay(); // purge previous screen
  display.setCursor(0, 0); // reset cursor position
  for (int i = 0; i < messageLength; i++) {
    display.write(messageCharArray[i]); // loop piping text on screen
  }
  display.display(); // execute render
}
