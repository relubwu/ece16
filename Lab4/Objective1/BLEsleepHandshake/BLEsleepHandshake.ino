/********************************************************************************
** Read from BLE and display on OLED
** Send symbol to BLE when connected
** The BLE toggles between sleep and awake when the button is pressed
** Updated handshake
*********************************************************************************/

// BT Library
#include <AltSoftSerial.h>
AltSoftSerial BTserial;

// Display Libraries
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#define OLED_RESET 4
Adafruit_SSD1306 display(OLED_RESET);

// Variables
char text[64];                                  // Character buffer
char c;
boolean asleep = false;
boolean confirmedCentral = false;


// Timing variables
unsigned long startTime = 0;
unsigned long endTime = 0;
const unsigned long period_us = 1e6;            // We are using microseconds for accuracy, 1s=1e6us


// Define pin numbers
const int buttonPin = 4;                        // Button pin

// --------------------------------------------------------------------------------
// Button logic: return true of the button is pressed, otherwise return false
// For more stable code, we can debounce the button
// --------------------------------------------------------------------------------
boolean checkButton() {
  static int buttonState = HIGH;                 // Pushbutton status
  if (digitalRead(buttonPin) != buttonState) {
    buttonState = !buttonState;
    if (buttonState == HIGH)
      return true;
  }
  return false;
}


// --------------------------------------------------------------------------------
// Initialize the OLED display
// --------------------------------------------------------------------------------
void initDisplay() {
  // Initialize with the I2C addr 0x3C (for the 128x32)
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.setTextColor(WHITE); // Draw white text, otherwise writes may be invisible!
  display.cp437(true);         // Use full 256 char 'Code Page 437' font
  display.setTextSize(1);      // Set font size for display.write() to 1
}



// --------------------------------------------------------------------------------
// Show a message on the OLED display
// --------------------------------------------------------------------------------
void showMessage(char message[]) {
  display.setCursor(0, 0);     // Start at top-left corner
  display.clearDisplay();
  display.println(message);
  display.display();
}



// --------------------------------------------------------------------------------
// Forward data from Serial to the BLE module
// This is useful to set the modes of the BLE module
// --------------------------------------------------------------------------------
void forwardSerialToBLE() {
  static boolean NL = true;

  c = Serial.read();
  if (c != 10 & c != 13 )  // do not send line end characters to the HM-10
    BTserial.write(c);
  // Copy the user input to the main window; if there is a new line print the ">" character.
  if (NL) {
    Serial.print("\r\n>");
    NL = false;
  }
  Serial.write(c);
  if (c == 10)
    NL = true;
}


// --------------------------------------------------------------------------------
// This function reads characters from the HM-10
// It's main goal is to detect if the central is sending "AT+..." indicating the handshake is not completed
// If a "T" is received right after an "A", we send back the handshake confirmation
// The function always returns the new character
// --------------------------------------------------------------------------------
char receiveFromBLE() {
  static char lastChar;

  char newChar = BTserial.read();
  switch (newChar) {
    case 'A':                                       // Starting AT Command reading
      lastChar = newChar;
      break;
    case 'T':                                       // AT was received
      if (lastChar == 'A') {
        BTserial.write("PeripheralConnected");
        Serial.print("PeripheralConnected");
        delay(50); BTserial.flushInput();           // Purge buffer
        confirmedCentral = true;
        lastChar = 0;
      }
      newChar = 0;                                  // This will clear the display
      break;
    default:                                        // Receiving data
      lastChar = newChar;
  }
  return newChar;
}




// --------------------------------------------------------------------------------
// Toggle BLE sleep state
// --------------------------------------------------------------------------------
void BLEConnect() {
  // Disconnect and put to sleep
  if (!asleep) {
    BTserial.print("AT");
    delay(150);
    BTserial.print("AT+ADTY3");
    delay(50);
    BTserial.print("AT+SLEEP");
    asleep = true;
    confirmedCentral = false;
  }
  // Wake up and re-establish connection
  else {
    BTserial.print("AT+galliaestomnisdivisainpartestresquarumunamincoluntbelgaealiamaquitanitertiamquiipsorumlinguaceltaenostragalliappellantur");
    delay(350);
    BTserial.print("AT+ADTY0");
    delay(50);
    BTserial.print("AT+RESET");
    asleep = false;
  }
}


// --------------------------------------------------------------------------------
// Setup: executed once at startup or reset
// --------------------------------------------------------------------------------
void setup() {
  // Initialize the OLED display
  initDisplay();
  showMessage("Initializing ...");
  delay(1000);

  // Initialize Serial (needed for setting the mode of the BLE)
  Serial.begin(9600);

  // Initialize the BT Serial (AltSoftSerial)
  BTserial.begin(9600);
  Serial.println("BTserial started");

  // Clear the display
  showMessage(" ");
}


// --------------------------------------------------------------------------------
// Loop: main code; executed in an infinite loop
// --------------------------------------------------------------------------------
void loop() {

  // Check if the button was pressed
  // If it was, establish or re-establish a BT connection
  if (checkButton())
    BLEConnect();

  // If we are asleep, do nothing until the button is pressed again
  if (!asleep) {    
    
    // Read from the Bluetooth module and store in a char array
    int i = 0;
    while (BTserial.available()) {
      text[i++] = receiveFromBLE();
      delay(10);                        // Allow time for new characters to come in
    }

    // If a new message was received, show it
    if (i > 0) {
      showMessage(text);
      Serial.println(text);
    }

    // Read from the Serial Monitor and send to the Bluetooth module
    if (Serial.available())
      forwardSerialToBLE();

    // If we received a message from the computer, we know we are connected. Start sending data back
    if (confirmedCentral) {
      endTime = micros();
      if (endTime - startTime >= period_us) {
        startTime = endTime;
        BTserial.print("*;");               // Added the ';' termination character
        Serial.println("*;");
      }
    }
  }
  
}
