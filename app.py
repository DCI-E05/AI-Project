import sys
from PySide6 import QtGui
from PySide6.QtCore import QThread, Qt, Signal, Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication, QLabel, QPushButton
from PySide6.QtGui import QPixmap
import cv2
import numpy as np


class CameraThread(QThread):
    change_frame = Signal(np.ndarray)

    def __init__(self):
        """Initialize parent's __init__() method and set the run flag of instance"""
        super().__init__()
        self._run_flag = True
        self.cap = cv2.VideoCapture(0)

    def run(self) -> None:

        while self._run_flag:
            success, img = self.cap.read()
            if success:
                self.change_frame.emit(img)
        self.cap.release()

    def stop(self):
        """Termiantes the QThread and wait until proccess will be closed"""
        self._run_flag = False
        self.wait()

class VideoChat(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setFixedSize(900, 900)
        self.setWindowTitle('GPT Video Chat')

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignHCenter)

        self.title = QLabel(text="Video Chat with GPT")
        self.title.setAlignment(Qt.AlignHCenter)
        self.title.setStyleSheet("""font-size: 50px;
text-align: center;
color: maroon;""")

        self.camera_image = QLabel()
        self.camera_image.setFixedSize(640, 320)
        self.camera_image.setStyleSheet("""border: 5px solid maroon;
border-radius: 13px;""")


        self.camera_thread = CameraThread()
        self.camera_thread.change_frame.connect(self.update_image)

        self.start_button = QPushButton(text='Start')
        self.start_button.setFixedHeight(60)
        self.start_button.setStyleSheet("""border: 3px solid black;
border-radius: 13px;
""")
        self.start_button.clicked.connect(self.start_camera)

        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.camera_image)
        self.main_layout.addWidget(self.start_button)


        self.setLayout(self.main_layout)
        self.show()


    def start_camera(self):
        self.camera_thread.start()

    @Slot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.camera_image.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


if __name__ == '__main__':
    app = QApplication([])
    widget = VideoChat()
    sys.exit(app.exec())



