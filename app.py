import sys
from PySide6 import QtGui
from PySide6.QtCore import QThread, Qt, Signal, Slot, QSize
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QApplication, QLabel, QPushButton, QTextEdit, QCheckBox
from PySide6.QtGui import QPixmap, QImage, QFont
from pydub import AudioSegment
from pydub.playback import play
import markdown
import cv2
import numpy as np
from object_recognition import prepare_image
from names import classes


# pip install PySide6

class SoundPlayer(QThread):
    finished = Signal(bool)

    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name

    def run(self):
        audio = AudioSegment.from_file(self.file_name, format="mp3")
        play(audio)
        self.finished.emit(True)

class CameraThread(QThread):
    change_frame = Signal(np.ndarray)
    results = Signal(list)
    bboxes = False

    def __init__(self):
        """Initialize parent's __init__() method and set the run flag of instance"""
        super().__init__()
        self._run_flag = True
        self.cap = cv2.VideoCapture(0)

    def run(self):

        while self._run_flag:
            success, img = self.cap.read()
            if success:
                # FINISH WORKABILITY OF CHECKBOX
                frame, results = prepare_image(img, classes, draw_results=True)
                self.results.emit(results)
                self.change_frame.emit(frame)
        self.cap.release()

    def stop(self):
        """Termiantes the QThread and wait until proccess will be closed"""
        self._run_flag = False
        self.wait()

class VideoChat(QWidget):
    def __init__(self):
        super().__init__()
        self.__initial_sound_finished = False
        self.__on_frame = []
        
        self.setFixedSize(900, 900)
        self.setWindowTitle('GPT Video Chat')
        self.setStyleSheet('''QWidget {background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #240068, stop: 1 #060060); }''')

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignHCenter)

        self.submain_layout = QHBoxLayout()
        self.submain_layout.setAlignment(Qt.AlignCenter)

        self.font = QFont("Helvetica", 20)

        self.title = QLabel(text="Video Chat with GPT")
        self.title.setFont(self.font)
        self.title.setAlignment(Qt.AlignHCenter)
        self.title.setStyleSheet("""font-size: 30px;
text-align: center;
color: maroon;
background-color: none;""")

        
        # Displays group
        self.camera_image = QLabel()
        self.camera_image.setFixedSize(640, 360)
        # self.camera_image.setScaledContents(True)
        self.camera_pixmap = QPixmap('./icons/camera-off.png')
        scaled = self.camera_pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.camera_image.setPixmap(scaled)
        self.camera_image.setAlignment(Qt.AlignCenter)
        self.camera_image.setStyleSheet("""border: 5px solid maroon;
border-radius: 13px;
background-color: black;""")

        
        self.chat_layout = QVBoxLayout()
        
        self.chat_browser = QTextEdit()
        self.chat_browser.setAcceptRichText(True)
        self.chat_browser.setFixedSize(640, 360)
        self.chat_browser.setReadOnly(True)
        html = markdown.markdown("# Welcome to chat with GPT!\ndfghfgh\ndfgh\ndfghd\nsadfgfasdfa\nfdgh\n\nasdfasdf\nsdfgs\ndfsgsdfg\nsdfgsdfgs\nsdfgsdfg\nsdfgsdfg\nsdfgasdfas")
        html = '\n'.join(classes)
        self.chat_browser.setText(html)
        self.chat_browser.setStyleSheet("""border: 5px solid maroon;
border-radius: 13px;
color: maroon;
text-align: center;
background-color: black;""")


        # CAMERA THREAD                                        
        self.camera_thread = CameraThread()
        self.camera_thread.change_frame.connect(self.update_image)
        self.camera_thread.results.connect(self.update_results)

        # Buttons group
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setAlignment(Qt.AlignCenter)

        self.boxes_check = QCheckBox(text="Show bound boxes")
        self.boxes_check.setChecked(False)
        self.boxes_check.setStyleSheet('background: transparent;')
        self.boxes_check.clicked.connect(self.show_boxes)
        

        self.say_button_icon = QPixmap('./icons/microphone.png')
        self.say_button = QPushButton(text="Say")
        self.say_button.setIcon(self.say_button_icon)
        self.say_button.setIconSize(QSize(50, 50))
        self.say_button.setStyleSheet("""QPushButton {
border: 3px solid maroon;
border-radius: 13px;
color: maroon;
font-size: 20px;
background-color: black;
}

QPushButton:hover {
border: 4px solid white;
background-color: black;
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
background-color: black;
}

QPushButton:hover {
border: 4px solid white;
}

QPushButton:disabled {
border: 2px solid rgba(83, 1, 1, 0.69);
blur(10px);
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
background-color: black;
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
        self.buttons_layout.addWidget(self.boxes_check)
        self.buttons_layout.addWidget(self.call_button)
        self.buttons_layout.addWidget(self.say_button)
        self.buttons_layout.addWidget(self.exit_button)
        

        # self.main_layout.addWidget(self.start_button)

        self.setLayout(self.main_layout)
        self.show()

    def show_boxes(self):
        if self.boxes_check.isChecked():
            CameraThread.bboxes = False
        else:
            CameraThread.bboxes = True
            

    def start_camera(self):
        self.camera_thread.start()
        self.play_calling_sound = SoundPlayer('./sounds/call-ring.mp3')
        self.play_calling_sound.finished.connect(self.change_state_of_camera)
        self.play_calling_sound.finished.connect(self.play_calling_sound.deleteLater)
        self.play_calling_sound.start()
        self.call_button.setEnabled(False)

    def change_state_of_camera(self):
        self.play_accepted_call = SoundPlayer('./sounds/notification-on.mp3')
        self.play_accepted_call.finished.connect(self.play_accepted_call.deleteLater)
        self.play_accepted_call.start()
        self.__initial_sound_finished = True

    @Slot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        if self.__initial_sound_finished:
            qt_img = self.convert_cv_qt(cv_img)
            self.camera_image.setPixmap(qt_img)
        elif not self.__initial_sound_finished:
            blured_image = cv2.blur(cv_img, ksize=(35, 35))
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = "Calling..."
            textsize = cv2.getTextSize(text, font, 1, 2)[0]
            textX = (blured_image.shape[1] - textsize[0]) // 2
            textY = (blured_image.shape[0] + textsize[1]) // 2
            cv2.putText(blured_image, text, (textX, textY), font, 1.5, (0, 255, 0), 5)
            qt_img = self.convert_cv_qt(blured_image)
            self.camera_image.setPixmap(qt_img)

    
    @Slot(list)
    def update_results(self, results):
        self.__on_frame = results
        # print(self.__on_frame)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
    def exit_app(self):
        self.exit_sound = SoundPlayer('./sounds/notification-off.mp3')
        self.exit_sound.start()
        self.exit_sound.wait()
        self.camera_thread.stop()
        self.close()


if __name__ == '__main__':
    app = QApplication([])
    widget = VideoChat()
    sys.exit(app.exec())



