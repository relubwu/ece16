Baichuan Wu </br>
A15608204 </br>

# Lab7

## Introduction
This lab integrates previous labs and appends IMU data handling capabilities

## Objective1
  1. **Goal**: Peak detection, Step counting
  2. **Steps**:
    * Merge ```Pedometer``` class
    * Wrap ```process()``` method with heuristics and peak detection to count steps
    * Repeatedly calling aforementioned methods to keep updating results
    * A video [demonstration link](https://drive.google.com/open?id=1NywTtzzl_sgk-HU-awvS5NOoKBX5E__K)

## Objective2
  1. **Goal**: Send HR and pedometer info to the Arduino
  2. **Steps**:
    * Modify and insert a call to ```bt.ble_write()``` every time calling ```update_data()``` to transmit data backward to Arduino
    * Display data onto OLED
    * A video [demonstration link](https://drive.google.com/open?id=1G47fR5XwRz9-rc53TlTSygajftKjFQnD)

## Objective3
  1. **Goal**: Vibrating Motor
  2. **Steps**:
    * Modify and insert a call to ```bt.ble_write()``` every time calling ```update_data()``` to transmit data backward to Arduino
    * Display data onto OLED
    * A video [demonstration link](https://drive.google.com/open?id=1G47fR5XwRz9-rc53TlTSygajftKjFQnD)

## Objective4
  1. **Goal**: Improvements
  2. **Steps**:
    * Our current heuristics for bpm utilizes the average interval between signals to eliminate outlier and thus acquire number of labels within a specific data chunk, then calculate it against the timespan of the chunk to resolve bpm. However, this algorithm can't handle situations where static data is passed in, therefore we might need another threshold gate to deactivate it when no pulse detected, as the ```is_active()``` does for pedometer
    * Our current heuristics for pedometer utilizes the peak detection api ```find_peaks()``` of ```scipy.signal```. However, the width and prominence are now being set fixed, maybe we could dynamically calculate these two parameters for different scenarios to generate better results. 

## Conclusion
Objectives completed, HR BPM recognition implemented, IMU data comm and processing fulfilled, pedometer KNN model traning tested.
