import torch
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
from PyQt5.QtCore import QObject,pyqtSignal, pyqtSlot
from settings import AppSettings
from database import Person


class FaceDetector(QObject):
    "Singleton face detector class"
    def __init__(self):
        super().__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.mtcnn = None
        self.settings = AppSettings()
        self.mtcnn = MTCNN(image_size=160, margin=20, device = self.device, keep_all =True)

    def detect_faces(self, image):
        return self.mtcnn.detect(image)

    def align_single(self, image):
        return self.mtcnn(image)[0]

    def align_multiple(self,image):
        return self.mtcnn(image)

    def align_to_np(self,image):
        tensor = self.align_single(image)
        if tensor is None:
            return np.zeros((160,160,3),np.uint8)
        return ((tensor.permute(1,2,0).cpu().numpy() * 128) +127.5).astype(np.uint8).copy()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FaceDetector, cls).__new__(cls)
        return cls.instance


class InceptionResnetV1Recognizer(QObject):
    def __init__(self,database):
        super().__init__()
        self.settings = AppSettings()

        self.database = database
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        #database change event
        self.database.databaseChanged.connect(self.initialize_encodings)

        print(self.device)
        self.resnet = InceptionResnetV1(pretrained='vggface2', device=self.device).eval()
        self.detector = FaceDetector()

        self.db_encodings = None
        self.initialize_encodings()

    
    def recognize_all(self, image):
        default = Person()
        encodings = self._get_encodings(image)
        if encodings is None:
            return [default]
       
        items=self.db_encodings.items()
        if len(items)==0:
            return [default]
        persons=[]
        for encoding in encodings:
            distances_w_ids = [(id, torch.pairwise_distance(encoding,kenc).detach().numpy()) for id,kenc in items]
            distances = np.array([d for _,d in distances_w_ids])
            index = np.argmin(distances)
            id,mindist = distances_w_ids[index]
            if mindist > self.settings.threshold:
                persons.append(default)
            else:
                person = self.database.get_person_by_id(id)
                persons.append(person)
        return persons

    def recognize_single(self, image):
        default = Person()
        encoding = self._get_encoding(image)
        if encoding is None:
            return default
        
        items=self.db_encodings.items()
        if len(items)==0:
            return default
        distances_w_ids = [(id, torch.pairwise_distance(encoding,kenc).detach().numpy()) for id,kenc in items]
        distances = np.array([d for _,d in distances_w_ids])
        index = np.argmin(distances)
        id,mindist = distances_w_ids[index]
        if mindist > self.settings.threshold:
            return default
        else:
            person = self.database.get_person_by_id(id)
            return person


    def _get_encodings(self, image):
        imgs_cropped = self.detector.align_multiple(image)
        if imgs_cropped is None:
            return None
        return self.resnet(imgs_cropped.to(self.device)).cpu()

    def _get_encoding(self, image):
        imgs_cropped =self.detector.align_single(image)
        if imgs_cropped is None:
            return None
        return self.resnet(imgs_cropped.unsqueeze(0).to(self.device)).cpu()

    def initialize_encodings(self):
        persons = self.database.get_all()
        encodings = {}
        for p in persons:
            encodings[p.id] = self._get_encoding(p.img)
        self.db_encodings = encodings
