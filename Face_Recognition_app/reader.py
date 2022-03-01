from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import serial
from serial.tools import list_ports
from messages import MessageContainer, Message

class RC522Reader(QThread):
    new_card = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.message = MessageContainer()
        self.serial = None
        self.last_id = None
        self._enable_reading = False
        self.init_reader()
        

    def run(self):
        while True:
            if self.serial is not None:
                try:
                    data = self.serial.readline()
                    data = data.decode("utf-8").strip()
                    print("recived from reader: "+data)
                    if self._enable_reading:
                        self.last_id = data
                        self.new_card.emit(data)
                except serial.SerialException as e:
                    print("An error occured, try reload reader: ", e)
                    self.serial =None
   
            else:
                print("Please connect reader")
                self.init_reader()
                self.sleep(1)
            self.sleep(0.5)   
            

    def get_last_id(self):
        return self.last_id

    def enable_reading(self):
        self._enable_reading = True

    def disable_reading(self):
        self._enable_reading = False
        self.last_id = None

    def init_reader(self):
        ports = list_ports.comports()
        portnames= []
        for p in ports:
            port, desc, hwid = p
            portnames.append(port)
        print("Available ports:", portnames)
        try:
            if len(portnames) > 0:
                print("Trying to open port",portnames[-1])
                self.serial = serial.Serial(port = portnames[-1],baudrate= 115200)
        except serial.SerialException as e:
            print("Cannon initialize reader:",e)
