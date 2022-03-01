from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time
import database
import os
from database import SQLiteDatabase
from reader import RC522Reader
from settings import AppSettings
from messages import MessageContainer, Message
from  queue import Queue
gpio = True
try:
    import Jetson.GPIO as GPIO
except:
    gpio = False
    print("GPIO unavailable")



class Loсk():
    def __init__(self):
        self.door_pin = 12
        self.settings = AppSettings()
        self.messages = MessageContainer()
        try:
            if gpio:
                GPIO.setmode(GPIO.BOARD)
                GPIO.setup(self.door_pin, GPIO.OUT, initial=GPIO.LOW)
        except:
            print("error initializing GPIO")

    def open(self):
        try:
            if gpio:
                GPIO.output([self.door_pin], GPIO.HIGH)
            self.messages.put(Message("The door is open",(170,255,150),time.time(),self.settings.open_time))
            print("The door is open")
        except:
            print("error opening door")

    def close(self):
        try:
            if gpio:
                GPIO.output([self.door_pin], GPIO.LOW)
            self.messages.put(Message("The door is closed",(255,170,150),time.time(),3))
            print("The door is closed")
        except:
            print("error closing door")


class LoсkThread(QThread):
    def __init__(self, db, recognizer,reader, frame_queue:Queue):
        super().__init__()
        self.settings = AppSettings()
        self.reader = reader
        self.look = Loсk()
        self.messages = MessageContainer()
        self.db= db 
        self.recognizer =  recognizer
        self.queue = frame_queue

        #will change this later
        self.default = database.Person().name
        self.reader.start()


    def run(self):
        while True:
            if not self.queue.empty():
                image = self.queue.get_nowait()
                if self.settings.mode == "multiple":
                    persons = self.recognizer.recognize_all(image)
                    self.process_multiple(persons)

                if self.settings.mode == "single":
                    person = self.recognizer.recognize_single(image)
                    self.process_single(person)
            self.sleep(1)

    def process_single(self,person):
        if person.name == self.default:
            print("Access denied: person wasn't recognized")
            self.messages.put(Message("Access denied: person wasn't recognized",(255,150,150),time.time(),3))
            self.sleep(3)
            #Message access denied
            return
        print(f"Person recognized as {person.name}")
        self.messages.put(Message(f"Person recognized as: {person.name}",(150,255,150),time.time(),10))
        self.reader.enable_reading()
        print("Please provide your card")
        self.messages.put(Message("Please scan your card",(150,150,255),time.time(),self.settings.wait_time))

        card_id = None
        for i in range(self.settings.wait_time):
            card_id = self.reader.get_last_id()
            if card_id is not None:
                break
            self.sleep(1)
        self.reader.disable_reading()
        if card_id is None:
            print("Timeout over but card was not present")
            self.messages.put(Message("Timeout over but card was not present",(255,150,150),time.time(),5))
            #Message that timeout end
            self.sleep(3)
            return
        if card_id == person.cardId:
            self.messages.put(Message(f"Access confirmed for {person.name}",(150,255,150),time.time(),5))
            self.look.open()
            self.sleep(self.settings.open_time)
            self.look.close()
            return
        else:
            self.messages.put(Message(f"Access denied: card didn't match",(255,100,150),time.time(),5))
            print("Access denied: card didn't match")

    def process_multiple(self, persons):
        names = [p.name for p in persons]
        print("Recognized persons: ",names)
        if self.default not in names:
            self.messages.put(Message("Access confirmed for all persons",(150,255,150),time.time(),5))
            self.look.open()
            self.sleep(self.settings.open_time)
            self.look.close()
            return
        else:
            print("Access denied")
            self.messages.put(Message("Access denied",(255,150,150),time.time(),5))
            self.sleep(3)
            #Message that not all persons was recognized
            return



