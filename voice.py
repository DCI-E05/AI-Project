import speech_recognition as sr

# install 'sudo apt install python3-pyaudio'


def speech_to_text(m: sr.Microphone, r: sr.Recognizer):
    with m as source:
        print("Speak something...")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return False
        except sr.RequestError as e:
            return False