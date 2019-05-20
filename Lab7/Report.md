Baichuan Wu </br>
A15608204 </br>

# Lab7

## Introduction
This lab integrates previous labs and appends IMU data handling capabilities

## Objective1
  1. **Goal**: Heart rate system integration
  2. **Steps**:
    * Modify and integrate ```hr_heuristics()``` method
      * Count timespan for beats
      * Average the timespan
      * Neglect outlier beats that have significantly smaller (greater then 2 standard deviation) timespan to its neighbors
      * Calculate and return bpm
    * Transmit data using BLE from Arduino, filter data
    * Live plot on Python
    * A video [demonstration link](https://drive.google.com/open?id=1rv5xHq3PWrQ1v9nz5AHxNYwvESO6w5ux)

## Conclusion
