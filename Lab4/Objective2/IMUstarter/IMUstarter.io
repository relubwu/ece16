/********************************************************************************
** IMU starter code
*********************************************************************************/

// IMU Libraries
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#include "Wire.h"


// IMU data variables
int16_t ax, ay, az, tp, gx, gy, gz;

// Timing variables
unsigned long startTime = 0;
unsigned long endTime = 0;
const int sampling_rate = 20;                             // Sampling rate in Hz
const unsigned long period_us = 1e6 / sampling_rate;      // Sampling period in micro seconds


// Define pin numbers
const int interruptPin = 2;   
volatile bool imuDataReady = false;


// IMU Setup 
const int MPU_addr = 0x68;                      // I2C address of the MPU-6050
MPU6050 IMU(MPU_addr);                          // Instantiate IMU object




// --------------------------------------------------------------------------------
// Function to check the interrupt pin to see if there is data available in the MPU's buffer
// --------------------------------------------------------------------------------
void interruptPinISR() {
  // Indicate data is ready
  ipinReady = true;
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
// Setup: executed once at startup or reset
// --------------------------------------------------------------------------------
void setup() {

  // Initialize the IMU
  initIMU();

  // Initialize Serial
  Serial.begin(9600);

}


// --------------------------------------------------------------------------------
// Loop: main code; executed in an infinite loop
// --------------------------------------------------------------------------------
void loop() {

      endTime = micros();
      if (endTime - startTime >= period_us) {
      
        startTime = endTime;
     
        // If the IMU has data, as indicated by the interrupt
        if (imuDataReady) {
          readIMU();
          imuDataReady = false;
          
          Serial.print(ax);
          Serial.print(" ");
          Serial.print(ay);
          Serial.print(" ");
          Serial.println(az);
        }
      }

}
