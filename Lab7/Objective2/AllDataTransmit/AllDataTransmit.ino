/********************************************************************************
** Read from BLE and display on OLED
** Read ax from the IMU and send over BLE
** The BLE toggles between sleep and awake when the button is pressed
** It uses the updated handshake
*********************************************************************************/

// BT Library
#include <AltSoftSerial.h>
AltSoftSerial BTserial;

// Display Libraries
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#define OLED_RESET 4
Adafruit_SSD1306 display(OLED_RESET);

// IMU Libraries
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#include "Wire.h"

// Text variables
char out_text[32];                            // Character buffer
char in_text[64];                             // Character buffer
bool newData;                                 // Flag for data recieved from Python
char imu_text[7];                              // 0-900000 + null char = 7 chars
char ir_text[7];                              // 0-900000 + null char = 7 chars
char time_text[9];                             // 5 chars to left of dot, the dot, 2 chars to right of dot + null char = 9 chars
char c;                                       // Used for forwardSerialToBLE()

// State variables
boolean asleep = false;
boolean confirmedCentral = false;

// IMU data variables
int16_t ax, ay, az, tp, gx, gy, gz;

// IR sensor variable
int sensorValue = 0; 

// Timing variables
unsigned long startTime = 0;
unsigned long endTime = 0;
const int sampling_rate = 20;                             // Sampling rate in Hz
const unsigned long period_us = 1e6 / sampling_rate;      // Sampling period in micro seconds


// Define pin numbers
const int buttonPin = 4;                        // Button pin
const int ledPin =  13;                         // LED pin
const int interruptPin = 2;
const int sensorPin = A1;    // select the input pin for the potentiometer
volatile bool imuDataReady = false;

// IMU Setup
const int MPU_addr = 0x68;                      // I2C address of the MPU-6050
MPU6050 IMU(MPU_addr);                          // Instantiate IMU object

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
// --------------------------------------------------------------------------------c
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
void showMessage(const char * message) {
  display.setCursor(0, 0);     // Start at top-left corner
  display.clearDisplay();
  display.println(message);
  display.display();
}

// --------------------------------------------------------------------------------
// Function to check the interrupt pin to see if there is data available in the MPU's buffer
// --------------------------------------------------------------------------------
void interruptPinISR() {
  // Indicate data is ready
  imuDataReady = true;
}

// --------------------------------------------------------------------------------
// Initialize the IMU
// --------------------------------------------------------------------------------
void initIMU() {

  // Intialize the IMU and the DMP (Digital Motion Processor) on the IMU
  IMU.initialize();
  IMU.dmpInitialize();
  IMU.setDMPEnabled(true);

  // Initialize I2C communications
  Wire.begin();
  Wire.beginTransmission(MPU_addr);
  Wire.write(MPU_addr);               // PWR_MGMT_1 register
  Wire.write(0);                      // Set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);

  // Create an interrupt for pin2, which is connected to the INT pin of the MPU6050
  pinMode(interruptPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(interruptPin), interruptPinISR, RISING);
}

// --------------------------------------------------------------------------------
// Forward data from Serial to the BLE module
// This is useful to set the modes of the BLE module
// --------------------------------------------------------------------------------
void forwardSerialToBLE() {
  static boolean NL = true;
  while (Serial.available()) {
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
    delay(5);
  }
}


// --------------------------------------------------------------------------------
// This function reads characters from the HM-10
// It's main goal is to detect if the central is sending "AT+..." indicating the handshake is not completed
// If a "T" is received right after an "A", we send back the handshake confirmation
// The function always returns true if ";" is received, indicating a complete message from Python has been received.
// The rest of the functionality is to prevent overflows
// --------------------------------------------------------------------------------
bool receiveFromBLE() {
  static char lastChar;
  static int i = 0;

  char newChar = BTserial.read();

  if (lastChar == 'A' && newChar == 'T') {
    BTserial.write("#");                          // Python uses "#" as a confirmation that the connection was succesful
    confirmedCentral = true;                      // Set Arduino-side flag for successful connection
    delay(50);                                    // Ensure all remaining handshake text has been received
    showMessage(" ");                             // Clear OLED display
    BTserial.flushInput();                        // Purge BLE buffer
    lastChar = 0; i = 0;                          // Reset receiveFromBLE() logic
    return false;                                 // Return to main loop
  }
  if (i >= sizeof(in_text)-1) {
    i = 0;
    Serial.println("Received >64 bytes of data, buffer was reset");
  }
  if (newChar == ';') {
    in_text[i] = 0;
    i = 0;
    lastChar = 0;
    return true;
  }
  else {
    lastChar = newChar;
    in_text[i++] = newChar;
    return false;
  }
}


// --------------------------------------------------------------------------------
// Read from the IMU
// Currently, this reads 3 acceleration axis, temperature and 3 gyro axis.
// You should edit this to read only the sensors you end up using.
// For this, you need to edit the number of registers being requested and possibly the addresses themselves
// --------------------------------------------------------------------------------
void readIMU() {
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x3B);                         // Starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);

  Wire.requestFrom(MPU_addr, 14, true);      // Request a total of 14 registers

  // Accelerometer (3 Axis)
  ax = Wire.read() << 8 | Wire.read();      // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  ay = Wire.read() << 8 | Wire.read();      // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  az = Wire.read() << 8 | Wire.read();      // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)

  // Temperature
  tp = Wire.read() << 8 | Wire.read();      // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)

  // Gyroscope (3 Axis)
  gx = Wire.read() << 8 | Wire.read();      // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  gy = Wire.read() << 8 | Wire.read();      // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  gz = Wire.read() << 8 | Wire.read();      // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
}

// --------------------------------------------------------------------------------
// Toggle BLE sleep state
// --------------------------------------------------------------------------------
void BLEConnect() {
  // Disconnect and put to sleep
  if (!asleep) {
    BTserial.print("OK+LOST");              // Just in case it doesn't get written before going to sleep
    delay(50);
    BTserial.print("AT");
    delay(150);
    BTserial.print("AT+ADTY3");
    delay(50);
    BTserial.print("AT+SLEEP");
    delay(50);
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
    delay(50);
    BTserial.flushInput();                      // Purge buffer
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

  // Initialize the IMU
  initIMU();

  // Initialize the LED pin as an output:
  pinMode(ledPin, OUTPUT);

  // Initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT_PULLUP);

  // Initialize Serial (needed for setting the mode of the BLE)
  Serial.begin(9600);

  // Initialize the BT Serial (AltSoftSerial)
  BTserial.begin(9600);
  Serial.println("BTserial started");

  // Clear the display
  showMessage(" ");
}

// --------------------------------------------------------------------------------
// Normalize data
// --------------------------------------------------------------------------------
int32_t l1norm() {
  return abs(ax) + abs(ay) + abs(az);
}

// --------------------------------------------------------------------------------
// Loop: main code; executed in an infinite loop
// --------------------------------------------------------------------------------
void loop() {
  // Check if the button was pressed
  // If it was, establish or re-establish a BT connection
  if (checkButton())
    BLEConnect();

  // Check if Python is sending a message to the Arduino. Also checks for handshake.
  if (BTserial.available()) {
    // Read from the Bluetooth module and send to OLED, Serial
    if (receiveFromBLE()) {
      // If a new message was completed by receiving the ";" character, show it
      showMessage(in_text);
      Serial.println(in_text);
    }
  }

  // Read from the Serial Monitor and send to the Bluetooth module
  if (Serial.available())
    forwardSerialToBLE();

  // If we received a message from the computer, we know we are connected. Start sending data back
  if (confirmedCentral) {                              // This implicitly checks if BLE is asleep (confirmedCentral would be false if asleep==true)
    endTime = micros();
    if (endTime - startTime >= period_us) {
      startTime = endTime;

      // If the IMU has data, as indicated by the interrupt
      if (imuDataReady) {
        // Read IMU data
        readIMU();
        imuDataReady = false;
      
        // read the value from the sensor:
        sensorValue = analogRead(sensorPin);
  
        dtostrf(endTime / 1e6, 5, 2, time_text);               // Write the end time to the time data char array
        dtostrf(sensorValue, 6, 0, ir_text);                           // Write the IMU x axis data to the IMU data char array
        dtostrf(l1norm(), 12, 0, imu_text);                           // Write the IMU x axis data to the IMU data char array
        sprintf(out_text, "%s, %s, %s;", time_text, ir_text, imu_text);     // Combine char arrays and add coma, semicolon
  
        BTserial.print(out_text);
        Serial.println(out_text);                         // Enable this for debugging
      }
      
    }
  }
  
}
