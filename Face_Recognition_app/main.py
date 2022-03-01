import sys
from PyQt5.QtWidgets import  QApplication
from gui import MainWindow
from recognizer import InceptionResnetV1Recognizer
from database import SQLiteDatabase
from lock import LoсkThread
from video import VideoThread
from reader import RC522Reader
import queue as q
import lock
import database
import PIL



def main():
    db_path = "persons.db"
    #database.create_test_db(db_path)
    db = SQLiteDatabase(db_path)
    reader = RC522Reader()
    frame_queue = q.Queue(maxsize = 1)
    recognizer = InceptionResnetV1Recognizer(db)
    #QApp and GUI window
    app = QApplication(sys.argv)
    main_w = MainWindow(db,reader)
    
    video_thread = VideoThread(frame_queue)
    #Responds for main logic asociated with opening/closing look
    loсk_thread = LoсkThread(db,recognizer,reader,frame_queue)

    #connecting general events for handlers
    main_w.size_changed.connect(video_thread.change_size)
    #connecting handler for new camera frame
    video_thread.new_frame_change.connect(main_w.change_frame)

    main_w.show_full_screen()

    #starting threads
    loсk_thread.start()
    video_thread.start()
    #starting main app thread
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
   
