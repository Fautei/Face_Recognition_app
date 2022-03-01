import os
import json
from PyQt5.QtCore import QObject,pyqtSignal, pyqtSlot



class AppSettings(QObject):
    settings_changed = pyqtSignal()
    def __init__(self, ):
        super().__init__()
        self.possible_modes = ["single","multiple"]
        self.filename = "settings.json"
        self.threshold =  None
        self.mode = None
        self.open_time = None
        self.wait_time = None
        if not os.path.isfile(self.filename):
            self.threshold =  0.8
            self.mode = "multiple"
            self.open_time = 10.
            self.wait_time = 10
            self.save()
        else:
            self.load()
                

    def change_settings(self,ntresh, nmode, nopentime, nwitetime):
        #verify parameters
        if type(ntresh) is float and 0<ntresh<2.5:
            self.threshold =  ntresh
        else:
            #raise exception
            print("Threshold incorrect: expected 0...2.5")
        if type(nmode) is str and nmode in self.possible_modes:
            self.mode = nmode
        else:
            #raise exception
            print("Mode incorrect: expected \"single\",\"multiple\"")
        if type(nopentime) is float and nopentime > 0:
            self.open_time = nopentime
        else:
            #raise exception
            print("Opet time incorrect: expected >0")
        if type(nwitetime) is int and nwitetime > 0:
            self.wait_time = nwitetime
        else:
            #raise exception
            print("Card wait time incorrect: expected >0")
        self.save()
        

    def load(self):
        with open(self.filename,'r') as set:
                obj = json.load(set)
                self.threshold =  obj["Recognition threshold"]
                self.mode = obj["Working mode"]
                self.open_time = obj["Open time"]
                self.wait_time = obj["Wait time"]
    
    def save(self):
        with open(self.filename,'w') as set:
            json.dump({"Recognition threshold":self.threshold,
                        "Working mode": self.mode,
                        "Wait time": self.wait_time,
                        "Open time": self.open_time},set)
        print("settings saved")
        self.settings_changed.emit()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AppSettings, cls).__new__(cls)
        return cls.instance