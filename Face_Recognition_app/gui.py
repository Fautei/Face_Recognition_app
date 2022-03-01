from PyQt5 import  uic
from PyQt5.QtWidgets import  QApplication,QMainWindow
from PyQt5.QtCore import pyqtSignal,Qt,QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from recognizer import FaceDetector
from messages import Message, MessageContainer
from settings import AppSettings
from video import VideoThread
import database
import glob
import PIL
import numpy as np
import cv2 as cv2
import queue

try:
    from PyQt5.QtCore import QProcess, QSysInfo
    from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton
except ImportError:
    from PySide2.QtCore import QProcess, QSysInfo
    from PySide2.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton

class MainWindow(QMainWindow):
    size_changed = pyqtSignal(tuple)
    def __init__(self,db,reader):
        super(QMainWindow, self).__init__()
        self.settings = AppSettings()
        self.detector = FaceDetector()
        self.reader = reader
        self.db = db
        self.ui = uic.loadUi("ui/mainwindow.ui")
        self.ui.show()
        self.ui.setButton.clicked.connect(self.change_settings)
        
        #Responds for camera processing, drawing and face detecting
        self.image = None

    def change_settings(self):
        set= uic.loadUi("ui/settings.ui")
        set.show()
        set.threshSpin.setValue(self.settings.threshold)
        set.modeBox.setCurrentText( "Terminal only" if self.settings.mode == "multiple" else "RFID with terminal")
        set.timeSpin.setValue(self.settings.open_time)
        set.waitSpin.setValue(self.settings.wait_time)

        set.saveButton.clicked.connect(lambda : (self.settings.change_settings(set.threshSpin.value(),
                                                                         "multiple" if set.modeBox.currentText() == "Terminal only" else "single",
                                                                        set.timeSpin.value(),
                                                                        set.waitSpin.value() ), set.close()))
        set.cancelButton.clicked.connect(lambda: set.close())

        set.deleteButton.clicked.connect(lambda: (set.close(), self.delete_person()))
        set.addpersonButton.clicked.connect(lambda: (set.close(),self.add_person()))

        set.exec()
    
    def add_person(self):
        addpage= uic.loadUi("ui/addPerson.ui")
        addpage.show()

        addpage.addButton.clicked.connect(lambda : (self.db.add_person(database.Person(name= addpage.nameEdit.text(),
                                                                                     cardId=addpage.cardIdEdit.text(),
                                                                                     img = self._pil_from_qt(addpage.photoLabel.pixmap()))),
                                                                                     addpage.close(), self.add_person()))
        self.reader.enable_reading()
        self.reader.new_card.connect(addpage.cardIdEdit.setText)
        addpage.takephotoButton.clicked.connect(lambda :(addpage.photoLabel.setPixmap(self.pixmap_from_np(
                                                                                        self.detector.align_to_np(self.image)))))
        addpage.cancelButton.clicked.connect(lambda : addpage.close())

        p = QProcess()
        res = p.start('onboard')
        addpage.exec()
        print("keyboard closed")
        p.close()
        self.reader.disable_reading()

    def delete_person(self):
        persons = self.db.get_all()

        delpage = uic.loadUi("ui/deletePerson.ui")
        delpage.show()
        for p in persons:
            delpage.personsList.addItem(f"name: {p.name}, card id: {p.cardId}, added: {p.date}")

        delpage.deleteButton.clicked.connect(lambda : (self.db.remove(persons[delpage.personsList.currentRow()].id if len(persons)>0 else -1),delpage.close(),self.delete_person()))

        delpage.cancelButton.clicked.connect(lambda : delpage.close())
        delpage.exec()

    def pixmap_from_np(self, image):
        h, w,ch = image.shape
        bytesPerLine = w*ch
        image = QImage(image.data, w, h, bytesPerLine, QImage.Format_RGB888)
        return QPixmap.fromImage(image)
        
    def change_frame(self, image, render):
        self.image = image
        pixmap = self.pixmap_from_np(render)
        self.ui.Videolabel.setPixmap(pixmap)

    def _pil_from_qt(self, qpixmap):
        try:
            return PIL.Image.fromqpixmap(qpixmap)
        except:
            print("Error processing image")
            return None

    def show_full_screen(self):
        #self.ui.showFullScreen()
        self.ui.Videolabel.resize(self.ui.size())
        self.size_changed.emit((self.ui.Videolabel.size().width(),self.ui.Videolabel.size().height()))
        