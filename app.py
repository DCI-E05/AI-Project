import sys, json
from PySide6 import QtGui
from PySide6.QtCore import QThread, Qt, Signal, Slot, QSize, QThreadPool
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QApplication, QLabel, QPushButton, QTextEdit, QCheckBox, QComboBox
from PySide6.QtGui import QPixmap, QImage, QFont, QMovie
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import markdown2
import cv2
import time
import numpy as np
from object_recognition import prepare_image
from text_to_speech import TextToSpeech
from gpt_requests import ChatBot
from names import classes


# pip install PySide6 markdown2



class TextToSpeechThread(QThread):
    finished = Signal(bool)

    def __init__(self, role):
        super().__init__()
        self.tts = TextToSpeech(role)
        self.text = ''
    
    def set_text(self, new_text):
        self.text = new_text

    def set_voice(self, new_role):
        self.tts.set_voice(new_role)

    def run(self):
        self.tts.speak(self.text)
        self.finished.emit(True)

class SpeechToTextThread(QThread):
    finished = Signal(bool)
    recognized_text = Signal(str)

    def __init__(self, recog: sr.Recognizer, micro: sr.Microphone):
        super().__init__()
        self.recognizer = recog
        self.microphone = micro
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, 1)
        self.all_text = ""
        self._run_flag = True
        self.stopped = False

    def run(self):
        self.stop_micro = self.recognizer.listen_in_background(self.microphone, callback=self.process_audio)
        print("Listening...")
        # while not self.stopped:
        #     while self._run_flag:
        #         pass
        # self.stop_micro(wait_for_stop=False)
                    # audio = self.recognizer.listen(source, 10)
                    # audio = self.recognizer.record(source, 3)
                    # self.process_audio(audio)
                    # time.sleep(1)

    def process_audio(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio)
            self.all_text += f" {text}"
            # time.sleep(1)
            print("You said:", self.all_text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

    def start_listening(self):
        self._run_flag = True
        self.stopped = False
        self.start()

    def stop_listening(self):
        self.stop_micro(wait_for_stop=True)
        self.recognized_text.emit(self.all_text[1:])
        self.all_text = ""
        self._run_flag = False
        
    def stop(self):
        self.stopped = True
        self.quit()
    

class GPTThread(QThread):
    finished = Signal(bool)
    response = Signal(str)

    def __init__(self, role):
        super().__init__()
        self.user_input = ''
        self.role = role
        self.chatbot = ChatBot(self.role)
        
    def change_role(self, role):
        self.chatbot.set_role(role)

    def set_user_input(self, new_value):
        self.user_input = new_value

    def run(self):
        resp = self.chatbot.get_response(self.user_input)
        self.response.emit(resp)
        self.finished.emit(True)


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

    def __init__(self):
        """Initialize parent's __init__() method and set the run flag of instance"""
        super().__init__()
        self._run_flag = True
        self.cap = cv2.VideoCapture(0)
        self.model = cv2.dnn.readNetFromTensorflow('./model/ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph_V2.pb', './model/ssd_mobilenet_v2_coco_2018_03_29/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')
        self.object_recognizer = ObjectRecognizer()
        self.object_recognizer.results.connect(self.emit_results)
        self.recog_finished = bool(True)
        self.last_recognition_time = time.time() # track when the last recognition was done

    def run(self):
        while self._run_flag:
            success, img = self.cap.read()
            if success:
                current_time = time.time()
                if current_time - self.last_recognition_time >= 1:
                    self.object_recognizer.run(img, self.model)
                    self.last_recognition_time = current_time
                self.change_frame.emit(img)
        self.cap.release()

    @Slot(list)
    def emit_results(self, results):
        self.results.emit(results)


    def stop(self):
        """Termiantes the QThread and wait until proccess will be closed"""
        self._run_flag = False
        self.wait()


class ObjectRecognizer(QThread):
    finished = Signal(bool)
    results = Signal(list)

    def __init__(self):
        super().__init__()
        self.stop = False

    def set_image(self, frame, model):
        self._frame = frame
        self._model = model

    def run(self, frame, model):
        res = prepare_image(frame, classes, model)
        self.results.emit(res)
        self.finished.emit(True)

    def stop_thread(self):
        self.stop = True
        self.wait()


class JsonReader(QThread):
    finished = Signal(dict)

    def __init__(self):
        super().__init__()
    
    def run(self):
        with open('./roles.json') as json_file:
            roles = json.load(json_file)
        self.finished.emit(roles)

class VideoChat(QWidget):
    def __init__(self):
        super().__init__()
        with open('styles.json') as f:
            self.styles = json.load(f)
        self.__initial_sound_finished = False
        self.__on_frame = []

        self.microphone = sr.Microphone()
        self.recognizer = sr.Recognizer()
        self.speech_to_text_thread = SpeechToTextThread(self.recognizer, self.microphone)

        self.speech_to_text_thread.recognized_text.connect(self.listened_results)
        self.is_listening = False
        

        screen_width, screen_height = QApplication.primaryScreen().size().toTuple()

        x = (screen_width - 900) // 2
        y = (screen_height - 900) // 2
        
        self.setGeometry(x, y, 900, 900)
        self.setWindowTitle('GPT Video Chat')
        self.setStyleSheet('''QWidget {background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgb(63, 63, 63), stop: 1 rgb(76, 76, 76));}''')

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignHCenter)

        self.submain_layout = QHBoxLayout()
        self.submain_layout.setAlignment(Qt.AlignCenter)

        self.font = QFont("Helvetica", 20)

        self.title = QLabel(text="Video Chat with GPT")
        self.title.setFont(self.font)
        self.title.setAlignment(Qt.AlignHCenter)
        self.title.setStyleSheet(self.styles["title"])

        
        # Displays group
        self.camera_image = QLabel()
        self.camera_image.setFixedSize(640, 360)
        # self.camera_image.setScaledContents(True)
        self.camera_pixmap = QPixmap('./icons/camera-off.png')
        scaled = self.camera_pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.camera_image.setPixmap(scaled)
        self.camera_image.setAlignment(Qt.AlignCenter)
        self.camera_image.setStyleSheet(self.styles["camera_image"])

        
        self.chat_layout = QVBoxLayout()
        
        self.chat_browser = QTextEdit()
        self.chat_browser.setAcceptRichText(True)
        self.chat_browser.setFixedSize(640, 360)
        self.chat_browser.setReadOnly(True)
        md = markdown2.markdown("# Welcome to chat with GPT!", extras=["fenced-code-blocks", "tables", "break-on-newline"])
        self.chat_browser.setHtml(md)
        self.chat_browser.setStyleSheet(self.styles["chat_browser"])


        # CAMERA THREAD                                        
        self.camera_thread = CameraThread()
        self.camera_thread.change_frame.connect(self.update_image)
        self.camera_thread.results.connect(self.update_results)

        # Buttons group
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setAlignment(Qt.AlignCenter)

        # Combobox to chose the role
        self.roles_combobox = QComboBox()
        self.roles_combobox.setStyleSheet(self.styles["roles_combobox"])
        self.roles_combobox.setFixedHeight(50)
        self.json_read_thread = JsonReader()
        self.json_read_thread.finished.connect(self.apply_json)
        self.json_read_thread.run()
        self.roles_combobox.currentIndexChanged.connect(self.combobox_changed)
        # self.roles_combobox.currentIndexChanged.connect(self.set_avatar)
        
        self.avatar = QLabel()
        self.avatar.setFixedSize(200, 200)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setStyleSheet("background: none;")


        self.say_button_icon = QPixmap('./icons/microphone.png')
        self.say_button = QPushButton(text="Say")
        self.say_button.setIcon(self.say_button_icon)
        self.say_button.setIconSize(QSize(50, 50))
        self.say_button.setStyleSheet(self.styles["say_button"])
        self.say_button.setFixedSize(200, 100)
        self.say_button.clicked.connect(self.toggle_listening)


        self.call_button_icon = QPixmap('./icons/call.png')
        self.call_button = QPushButton(text='Call')
        self.call_button.setFixedHeight(60)
        self.call_button.setIcon(self.call_button_icon)
        self.call_button.setIconSize(QSize(50, 50))
        self.call_button.setStyleSheet(self.styles["call_button"])
        self.call_button.clicked.connect(self.start_camera)
        self.call_button.setFixedSize(200, 100)

        self.exit_button_icon = QPixmap('./icons/exit.png')
        self.exit_button = QPushButton(text='Exit')
        self.exit_button.setIcon(self.exit_button_icon)
        self.exit_button.setIconSize(QSize(50, 50))
        self.exit_button.clicked.connect(self.exit_app)
        self.exit_button.setStyleSheet(self.styles["exit_button"])
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
        self.buttons_layout.addWidget(self.avatar)
        self.buttons_layout.addWidget(self.roles_combobox)
        self.buttons_layout.addWidget(self.call_button)
        self.buttons_layout.addWidget(self.say_button)
        self.buttons_layout.addWidget(self.exit_button)
        

        # self.main_layout.addWidget(self.start_button)

        self.setLayout(self.main_layout)
        self.show()

        
    def toggle_listening(self):
        if not self.is_listening:
            self.speech_to_text_thread.start_listening()
            # self.speech_to_text_thread.finished.connect(self.speech_to_text_thread.deleteLater) 
            self.is_listening = True
            self.say_button.setText("Stop")
        else:
            self.speech_to_text_thread.stop_listening()
            self.is_listening = False
            self.say_button.setText("Say")
            if len(self.speech_result) > 0:
                self.say_button.setDisabled(True)
                self.speech_result += "[" + ", ".join(self.__on_frame) + "]"
                self.gpt_instace.set_user_input(self.speech_result)
                self.gpt_instace.start()


    @Slot(str)
    def listened_results(self, result):
        self.speech_result = result
        current_value = self.chat_browser.toMarkdown()
        if result:
            current_value += "\n\n**You:** " + "*" + result + "*"
            current_value += f"\n**Objects:** *" + ", ".join(self.__on_frame) + "*"
        else:
            current_value += "\n\n## Voice recognizer didn't got you! Try again."
        new_markdown = markdown2.markdown(current_value, extras=["fenced-code-blocks", "tables", "break-on-newline"])
        self.chat_browser.setHtml(new_markdown)
        self.say_button.setDisabled(False)
        self.chat_browser.ensureCursorVisible()

    @Slot(str)
    def retrieve_response(self, response):
        self.tts_thread.set_text(response)
        self.tts_thread.start()
        current_value = self.chat_browser.toMarkdown()
        current_value += f"\n\n**{self.roles_combobox.currentText()}**: " + response
        new_markdown = markdown2.markdown(current_value, extras=["fenced-code-blocks", "tables", "break-on-newline"])
        self.chat_browser.setHtml(new_markdown)
        self.chat_browser.ensureCursorVisible()

    def set_avatar(self):
        role = self.roles_combobox.currentText()
        if role == "Batman" or role == 'Batman Rogue':
            image = QPixmap("./roles_icons/batman.png")
        elif role == "Eminem":
            image = QPixmap("./roles_icons/eminem.png")
        elif role == "Crackhead":
            image = QPixmap("./roles_icons/crackhead.png")
        elif role == "Crusader":
            image = QPixmap("./roles_icons/crusader.png")
        elif role == "Markus":
            image = QPixmap("./roles_icons/Markus.png")
        elif role == "Employee-kaufland":
            image = QPixmap("./roles_icons/kaufland.png")
        elif role == "Mike Tyson":
            image = QPixmap("./roles_icons/tyson.png")
        if role != 'Choose a role...':
            self.avatar.setPixmap(image)
        self.avatar.setScaledContents(True)
    
    def set_movie(self):
        role = self.roles_combobox.currentText()
        if role == "Batman" or role == 'Batman Rogue':
            animation = QMovie("./roles_anims/batman.gif")
        if role == "Eminem":
            animation = QMovie("./roles_anims/eminem.gif")
        if role == "Crackhead":
            animation = QMovie("./roles_anims/crackhead.gif")
        if role == "Crusader":
            animation = QMovie("./roles_anims/crusader_anim.gif")
        if role == "Markus":
            animation = QMovie("./roles_anims/Markus.gif")
        if role == "Employee-kaufland":
            animation = QMovie("./roles_anims/kaufland.gif")
        if role == "Mike Tyson":
            animation = QMovie("./roles_anims/tyson.gif")
        self.avatar.setMovie(animation)
        animation.start()

    def tts_finished(self):
        self.say_button.setDisabled(False)

    @Slot(dict)
    def apply_json(self, roles):
        items = list(roles.keys())
        items.insert(0, "Choose a role...")
        self.roles_combobox.addItems(items)
        self.roles_dict = roles
        self.roles_combobox.setCurrentText("Choose a role...")
        self.json_read_thread.wait()
        self.gpt_instace = GPTThread(self.roles_dict['Batman'])
        self.gpt_instace.response.connect(self.retrieve_response)
        self.tts_thread = TextToSpeechThread("Batman")
        self.tts_thread.finished.connect(self.tts_finished)
            

    def combobox_changed(self):
        if not self.call_button.isEnabled():
            self.set_movie()
        else:
            self.set_avatar()
        self.avatar.setScaledContents(True)
            
        md = markdown2.markdown("# Welcome to chat with GPT!", extras=["fenced-code-blocks", "tables", "break-on-newline"])
        self.chat_browser.setText(md)
        new_role = self.roles_dict[self.roles_combobox.currentText()]
        self.gpt_instace.wait()
        self.tts_thread.wait()
        self.gpt_instace.change_role(new_role)
        self.tts_thread.set_voice(self.roles_combobox.currentText())

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
        self.set_movie()
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
        self.__on_frame = set(results)
        print(self.__on_frame)

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
        # self.gpt_instace.wait()
        # self.camera_thread.wait()
        # self.json_read_thread.wait()
        # self.tts_thread.wait()
        # self.speech_to_text_thread.wait()
        self.close()


if __name__ == '__main__':
    app = QApplication([])
    widget = VideoChat()
    sys.exit(app.exec())



