import speech_recognition as sr
import threading

class SpeechRecognizer:
    def __init__(self, is_conversing_event):
        self.recognizer = sr.Recognizer()
        self.is_conversing_event = is_conversing_event

    def recognize_speech(self):
        # if not self.is_conversing_event.is_set():
        #     return None

        with sr.Microphone() as source:
            print("Listening...")
            # if not self.is_conversing_event.is_set():
            #     return None
            audio = self.recognizer.listen(source)

        #if not self.is_conversing_event.is_set():
        #    return None

        try:
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio)
            return text 

        except sr.UnknownValueError:
            print("Could not understand audio. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
        
if __name__ == "__main__":  
    is_conversing_event = threading.Event()
    speech_recognizer = SpeechRecognizer(is_conversing_event)
    while True:
        is_conversing_event.set()
        recognized_text = speech_recognizer.recognize_speech()
        print(recognized_text)
