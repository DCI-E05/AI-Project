import speech_recognition as sr
from PySide6.QtCore import QThread, Signal

class SpeechToTextThread(QThread):
    text_recognized = Signal(str)

    def __init__(self, rec, mic):
        super().__init__()
        self.recognizer = rec
        self.micro = mic
        self._run_flag = True
        self.stopped = False

    def run(self):
        self.listen()

    def listen(self):
        with self.micro as source:
            while not self.stopped:
                while self._run_flag:
                    print("Listening...")
                    #audio = self.recognizer.listen(source, timeout=20)
                    audio = self.recognizer.record(source, 10)
                self.process_audio(audio)

    def process_audio(self, audio):
        try:
            text = self.recognizer.recognize_google(audio)
            print("You said: ", text)
            self.text_recognized.emit(text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(
                f"Could not request results from Google Speech Recognition service; {e}")

    def start_listening(self):
        self._run_flag = True
        self.stopped = False
        self.start()

    def stop_listening(self):
        self._run_flag = False
        
    def stop(self):
        self.stopped = True
        self.wait()
        self.quit()