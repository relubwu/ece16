Baichuan Wu </br>
A15608204 </br>

# Lab5

## Introduction
  * BLE Handshake
  * IMU Basics
  * Live Plotting
  * Saving and Replaying the data

## Objective1
  1. **Goal**: Voltage Divider, Analog Amplifier, Quantization
  2. **Steps**:
    * Assemble IR circuit
    ![IRcircuit1a](Images/IRcircuit1a.png)
    * Transmit & plot sensor data onto serial plotter
    ![Heartrate1a](Images/Heartrate1a.png)
    * **Observation**:
    Signal derived is heavily distorted and contains lot of noise, due to weak signal strength. But still a pattern can be observed, thus requires a denoise regression (quantization)
    * Upgrade circuit for better resolution
    ![IRcircuit1b](Images/IRcircuit1b.png)
    ![Heartrate1b](Images/Heartrate1b.png)

## Conclusion
Circuit assembled, IR sampling working
