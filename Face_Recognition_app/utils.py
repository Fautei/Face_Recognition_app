import pickle
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np

print(r"//\\")

print("привет"[0:1])

#device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#resnet = InceptionResnetV1(pretrained='vggface2').eval()
#resnet = resnet.to(device)
#mtcnn = MTCNN(image_size=160, margin=50)
#mtcnn = mtcnn.to(device)

#img_path = "image.13.jpg"
#img = Image.open(img_path)
#img_cropped = mtcnn(img)
#encoding = resnet(img_cropped.unsqueeze(0))

#with open("maxim.enc", "wb") as f:
#    torch.save(encoding,f)

#with open("maxim.enc", "rb") as f:
#    tensor = torch.load(f)
#    print(tensor)

    #def addPerson():
    #    name, status = QInputDialog.getText(QInputDialog(), 'Установка текста', 'Введите текст, например: Hello World')
    #    print(f"text={name}, status={status}")
    #    image = stream.CaptureImage()
    #    if name: 
    #        database.addPerson(image,name)


    #ui.addpersonButton.clicked.connect(addPerson)