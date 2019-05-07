# Imports
import serial
from time import sleep

class Bt:

    def __init__(self, ble_peripheral_MAC, serial_port, baudrate=9600):
        self.ble_peripheral_MAC = ble_peripheral_MAC
        self.baudrate = int(baudrate)
        self.serial_port = serial_port
        self.ble_conn = None

    def ble_setup(self):
        """
        Sets up BLE for the first time
        :return: None
        """
        print("Resetting connection")
        self.ble_conn = serial.Serial(port=self.serial_port, baudrate=self.baudrate, timeout=1)
        self.ble_write("AT")
        sleep(2)
        self.ble_flush()  # remove any connection lost messages

        finished = False
        step = 0
        attempts = 0

        while not finished:
            status = self.ble_read_buffer()

            if attempts > 20:
                print("Failed to connect, please check hardware.")
                raise IOError

            if "#" in status:
                print("Connection established and confirmed")
                break

            if "OK+Set" in status or "OK+CONNAOK+CONN" in status:
                step += 1

            if step == 0:
                self.ble_write("AT+IMME1")
                print("Setting connection mode")
                sleep(0.5)
            elif step == 1:
                self.ble_write("AT+NOTI1")
                print("Setting notification mode")
                sleep(0.5)
            elif step == 2:
                self.ble_write("AT+ROLE1")
                print("Setting BLE role")
                sleep(0.5)
            elif step == 3:
                self.ble_write("AT+CON" + self.ble_peripheral_MAC)
                print("Connecting to peripheral: ", self.ble_peripheral_MAC)
                sleep(0.5)
            elif step == 4:
                self.ble_write("AT+NAME?")
                print("Confirming connection handshake")
                sleep(1)
            else:
                print("Setup completed successfully")
                finished = True
        return

    def ble_read(self):
        """
        For compatibility with older versions of the library. Calls equivalent function in this version
        :return:
        """
        return self.ble_read_buffer()

    def ble_read_buffer(self):
        """
        Reads entire BLE buffer. If connection is lost, attempts to reconnect.
        :return: String containing data read from BLE buffer.
        """
        msg = ""
        try:
            if self.ble_conn.in_waiting > 0:
                msg = self.ble_conn.readline(self.ble_conn.in_waiting).decode("utf-8")
                # checks if a connection has been broken and tries to automatically reconnect
                attempts = 0
                while "OK+LOST" in msg and attempts < 10:
                    self.ble_setup()
                    print("Connection dropped, attempting to reconnect")
                    attempts = attempts + 1
                    msg = self.ble_conn.readline(self.ble_conn.in_waiting).decode("utf-8")
                if attempts >= 10:
                    print("Failed to reconnect, please check hardware.")
                    raise IOError
        except ValueError as error:
            print(error)
            return ""
        return msg

    def ble_read_line(self, eol='\n'):
        """
        Reads BLE buffer up until designated character. If connection is lost, attempts to reconnect.
        :param eol: character (single element string) containing delimiting character.
        :type eol: str
        :return: String containing data read from BLE buffer.
        """
        assert len(eol) == 1, "Delimiting character must be a single element string."
        assert isinstance(eol, str), "Delimiting character must be a string."
        msg = ""
        try:
            while True:
                c = ""
                while c != eol:
                    msg += c
                    c = self.ble_conn.read(1).decode("utf-8")

                attempts = 0
                while "OK+LOST" in msg and attempts < 10:
                    self.ble_setup()
                    print("Connection dropped, attempting to reconnect")
                    attempts = attempts + 1
                    msg = self.ble_conn.readline(self.ble_conn.in_waiting).decode("utf-8")
                if attempts >= 10:
                    print("Failed to reconnect, please check hardware.")
                    raise IOError
                return msg
        except ValueError as error:
            print(error)
            return ""

    def ble_write(self, message):
        self.ble_conn.write(message.encode("utf-8"))
        return

    def ble_flush(self):
        """
        Flushes BLE read/write buffer
        :return: None
        """
        self.ble_conn.flushInput()
        self.ble_conn.flushOutput()
        sleep(0.1)
        return

    def ble_close(self):
        """
        Ends (closes) BLE connection.
        :return: None
        """
        self.ble_conn.close()
        return
