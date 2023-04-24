import sys
from PySide6 import QtGui
from PySide6.QtCore import QThread, Qt, Signal, Slot, QSize
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QApplication, QLabel, QPushButton, QTextEdit
from PySide6.QtGui import QPixmap, QImage
import markdown
import cv2
import numpy as np


class CameraThread(QThread):
    change_frame = Signal(np.ndarray)

    def __init__(self):
        """Initialize parent's __init__() method and set the run flag of instance"""
        super().__init__()
        self._run_flag = True
        self.cap = cv2.VideoCapture(0)

    def run(self):

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
        self.setStyleSheet('background-color: black;')

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignHCenter)

        self.submain_layout = QHBoxLayout()
        self.submain_layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel(text="Video Chat with GPT")
        self.title.setAlignment(Qt.AlignHCenter)
        self.title.setStyleSheet("""font-size: 30px;
text-align: center;
color: maroon;""")

        
        # Displays group
        self.camera_image = QLabel()
        self.camera_image.setFixedSize(640, 360)
        self.camera_image.setStyleSheet("""border: 5px solid maroon;
border-radius: 13px;""")

        
        self.chat_layout = QVBoxLayout()
        
        self.chat_browser = QTextEdit()
        self.chat_browser.setAcceptRichText(True)
        self.chat_browser.setFixedSize(640, 360)
        self.chat_browser.setReadOnly(True)
        html = markdown.markdown("# This is header\n\n*This is bold*")
        self.chat_browser.setText(html)
        self.chat_browser.setStyleSheet("""border: 5px solid maroon;
border-radius: 13px;
color: maroon;
text-align: center;""")


        # CAMERA THREAD                                        
        self.camera_thread = CameraThread()
        self.camera_thread.change_frame.connect(self.update_image)

        # Buttons group
        self.buttons_layout = QVBoxLayout()

        self.say_button_icon = QPixmap('./icons/microphone.png')
        self.say_button = QPushButton(text="Say")
        self.say_button.setIcon(self.say_button_icon)
        self.say_button.setIconSize(QSize(50, 50))
        self.say_button.setStyleSheet("""QPushButton {
border: 3px solid maroon;
border-radius: 13px;
color: maroon;
font-size: 20px;
}

QPushButton:hover {
border: 4px solid white;
}
""")
        self.say_button.setFixedSize(200, 100)


        self.call_button_icon = QPixmap('./icons/call.png')
        self.call_button = QPushButton(text='Call')
        self.call_button.setFixedHeight(60)
        self.call_button.setIcon(self.call_button_icon)
        self.call_button.setIconSize(QSize(50, 50))
        self.call_button.setStyleSheet("""QPushButton {
border: 3px solid maroon;
border-radius: 13px;
color: maroon;
font-size: 20px;
}

QPushButton:hover {
border: 4px solid white;
}
""")
        self.call_button.clicked.connect(self.start_camera)
        self.call_button.setFixedSize(200, 100)

        self.exit_button_icon = QPixmap('./icons/exit.png')
        self.exit_button = QPushButton(text='Exit')
        self.exit_button.setIcon(self.exit_button_icon)
        self.exit_button.setIconSize(QSize(50, 50))
        self.exit_button.clicked.connect(self.exit_app)
        self.exit_button.setStyleSheet("""QPushButton {
border: 3px solid maroon;
border-radius: 13px;
color: maroon;
font-size: 20px;
}

QPushButton:hover {
border: 4px solid white;
}
""")
        self.exit_button.setFixedSize(200, 100)

        # Layouts
        # MAIN
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.submain_layout)

        # SUB MAIN
        self.submain_layout.addLayout(self.chat_layout)
        self.submain_layout.addLayout(self.buttons_layout)

        # CHAT
        self.chat_layout.addWidget(self.camera_image)
        self.chat_layout.addWidget(self.chat_browser)

        # BUTTONS
        self.buttons_layout.addWidget(self.call_button)
        self.buttons_layout.addWidget(self.say_button)
        self.buttons_layout.addWidget(self.exit_button)
        

        # self.main_layout.addWidget(self.start_button)


        self.setLayout(self.main_layout)
        self.show()


    def start_camera(self):
        self.camera_thread.start()

    @Slot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        self.image_to_process = cv_img
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
    
    def exit_app(self):
        self.camera_thread.stop()
        self.close()


if __name__ == '__main__':
    app = QApplication([])
    widget = VideoChat()
    sys.exit(app.exec())



