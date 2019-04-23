# Imports
import serial
from time import sleep

class Bt:

    def __init__(self, ble_peripheral_MAC, serial_port, baudrate=9600):
        self.ble_peripheral_MAC = ble_peripheral_MAC
        self.baudrate = int(baudrate)
        self.serial_port = serial_port
        self.ser = None
        print("Bt initialized")
      
    
    # Set up the BLE module        
    def ble_setup(self):
        print("Bt setup")
        #print("Resetting connection")
        self.ser = serial.Serial(port=self.serial_port, baudrate=self.baudrate, timeout=1)
       
        setup_commands = ["AT", "AT+IMME1", "AT+NOTI1", "AT+ROLE1"]

        connect_command = "AT+CON" + self.ble_peripheral_MAC

        # Send the setup commands
        for command in setup_commands:
            self.ble_write(command)
            print("Sent: " + command)
            sleep(0.5)
            response = self.ble_read()
            print("Response: " + response)
        
        # Keep sending the connect command until connection is established
        response = ""
        while not ("OK+CONNAOK+CONN" in response):
            self.ble_write(connect_command)
            print("Sent: " + connect_command)
            sleep(0.5)
            response = self.ble_read()
            print("Response: " + response)
        
        # Notify the Arduino we are connected
        sleep(1)
        handshake = False
        print("Confirming connection handshake")
        while not (handshake):
            self.ble_write("AT+NAME?")
            sleep(1)
            if "PeripheralConnected" in self.ble_read():
                handshake = True
                break
        
    # Read from BLE until a designated character is found
    def ble_read_line(self, eol='\n'):
        msg = ""
        c = ""
        while c != eol:
            msg += c
            c = self.ser.read(1).decode("utf-8")
        return msg
    
    
    # Read from serial ser and return the string that was read
    def ble_read(self):
        msg = ""
        in_wait = self.ser.in_waiting
        if in_wait > 0:
            try:
                msg = self.ser.readline(in_wait).decode("utf-8")
            except UnicodeDecodeError:
                msg = msg

        return msg


    # Write the string, command, to serial ser; return nothing
    def ble_write(self, message):
        print("try")
        self.ser.write(message.encode("utf-8"))
        return


    # Close the connection
    def ble_close(self):
        self.ser.close()
        return
    
