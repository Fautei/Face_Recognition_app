import sqlite3
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt,QObject, pyqtSignal, pyqtSlot
from datetime import datetime
import pickle
from PIL import Image
import PIL
import os
from messages import Message, MessageContainer
import time

class Person():
    def __init__(self, id =-1,cardId = "",name = "Unknown",img = None,date = datetime.now()):
        self.id = id
        self.cardId = cardId
        self.name = name
        self.img = img
        self.date = date
    
    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False
            
class SQLiteDatabase(QObject):
    """description of class"""
    databaseChanged = pyqtSignal()
    def __init__(self,database_path):
        super().__init__()
        self.messages = MessageContainer()
        self.sqlite_connection = sqlite3.connect(database_path,check_same_thread=False)
        self.cursor = self.sqlite_connection.cursor()
        
    def get_all(self):
        try:
            self.cursor.execute(''' SELECT * FROM persons 
            ''')
            return [Person(id,card,name,pickle.loads(img),date) for(id,card,name,img,date) in self.cursor.fetchall()]
        except:
            print("Exception occured while processing the request")
            return []


    def add_person(self, person):
        print(f"trying to add person: {person.name} to database: {person.date}")
        if(person.name=="" or person.cardId == "" or person.img == None):
            print("Incorrect values")
            #reise exception
            return
        binary = pickle.dumps(person.img,-1)
        try:
            self.cursor.execute(f'''INSERT INTO persons (cardId,name,image,registered_date)
                                VALUES ("{person.cardId}","{person.name}",?,"{datetime.now()}");''',(binary,))
            self.databaseChanged.emit()
            self.sqlite_connection.commit()
            
        except:
            self.messages.put(Message("Exception occured while processing the request",(255,150,150),time.time(),6))
            print("Exception occured while processing the request")
            return
        self.messages.put(Message(f"Person: {person.name} added to database",(170,255,150),time.time(),6))
        print(f"person: {person.name} added to database: {person.date}")

    def remove(self,id):
        if id == -1:
            print("Incorrect values")
            #reise exception
            return
        try:
            person = self.get_person_by_id(id)
            print(f"trying to remove {person.name} from database")
            self.cursor.execute(f'''DELETE FROM persons WHERE id={id}''')
            self.databaseChanged.emit()
            self.sqlite_connection.commit()
        except:
            self.messages.put(Message("Exception occured while processing the request",(255,150,150),time.time(),6))
            print("Exception occured while processing the request")
            return
        self.messages.put(Message(f"Person: {person.name} deleted from database",(255,130,150),time.time(),6))
        print(f"person: {person.name} deleted from database: {person.date}")

    def get_person_by_id(self,id):
        try:
            self.cursor.execute(f''' SELECT * FROM persons 
                                    WHERE id = {id}''')
        except:
            print("Exception occured while processing the request")
            return Person()
        persons = self.cursor.fetchall()
        if persons is None:
            return Person()
        for id,cardid,name,img,date in persons:
            return Person(id,cardid,name,pickle.loads(img),date)    
        

    def get_person_by_cardid(self,cardId):
        try:
            self.cursor.execute(f''' SELECT * FROM persons 
                                WHERE cardId = "{cardId}"''')
        except:
            print("Exception occured while processing the request")
            return Person()
        persons =self.cursor.fetchall()
        if persons is None:
            return Person()
        for id,cardid,name,img,date in persons:
            return Person(id,cardid,name,pickle.loads(img),date)    
        

def create_test_db(database_path):
    if os.path.isfile(database_path):
        return
    try:
        sqlite_connection = sqlite3.connect(database_path)
        cursor = sqlite_connection.cursor()

        cursor.execute('''CREATE TABLE persons (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                cardId TEXT NOT NULL,
                                name TEXT NOT NULL,
                                image TEXT NOT NULL,
                                registered_date datetime);''')
        sqlite_connection.commit()
        img = Image.open("image.13.jpg")
        binary = pickle.dumps(img,-1)

        cursor.execute(f'''INSERT INTO persons (cardId,name,image,registered_date)
                                VALUES ( "caafdcb","Maxim Ilyin",?,"{datetime.now()}");''',(binary,))

        sqlite_connection.commit()
        sqlite_connection.close()
    except:
        print("error while creating test db")
