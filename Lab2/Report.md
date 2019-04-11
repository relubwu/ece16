Baichuan Wu </br>
A15608204 </br>

# Lab2

## Introduction
  * Testing AT commands
  * Communicating with BLE
  * Sending information to an OLED display
  * Using a button to create a stopwatch
  * Soldering: OLED and button

## Objective1
  1. **Goal**: Arduino to BLE, AT Commands
  2. **Steps**:
    * Assemble HM-10 module to Arduino on breadboard
    * Install `AltSoftSerial` dependencies in Arduino IDE
    * Setup data transfer route between `SoftSerial` and `AltSoftSerial` in the main `loop()`
    * Upload compiled code
    * Test `AT+` commands
    ![Testing AT Commands](Images/objective1.png)

## Objective2
  1. **Goal**: Communicate with other BLE devices
  2. **Steps**:
    * Switch self to peripheral / central mode using `AT+ROLEx` command
    * Query MAC address using `AT+ADDR?` command
    * Connect to other devices using specific MAC address using `AT+CONx` command
    * Set connection mode to immediate if necessary using `AT+IMMEx` command
    * Transfer data
    ![Transferring data to others](Images/objective2a.png)
    * Switch roles using `AT+ROLEx` and repeat aforementioned processes

## Objective3a
  1. **Goal**: OLED Display Peripheral, I2C Protocol
  2. **Steps**:
    * Solder 4-header pins onto OLED panel
    * Attach OLED panel to the breadboard
    * Install `Wire` and `Adafruit` libraries
    * Setup text serial channel, styling in `setup()`
    * Whenever serial receives message, convert it to a `char[]` using `strcpy` to a designated `char[]*`
    * Pipe text using `display.write()` and `display.display()`
    * Clear display and reset cursor if necessary using `display.clearDisplay()` and `display.setCursor(0, 0)`
    ![OLED Board](Images/oled_board.png)


## Conclusion
  All objectives completed. IDE environment set up, solder practiced, first Arduino application created & tested, Github repository initialized.  
