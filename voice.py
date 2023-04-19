# install 'sudo apt install python3-pyaudio'

import speech_recognition as sr
import os

# Initialize recognizer
r = sr.Recognizer()

# Use microphone as audio source
with sr.Microphone() as source:
    os.system('clear')
    print("Speak something...")
    audio = r.listen(source)

# Recognize speech
try:
    text = r.recognize_google(audio)
    print("You said:", text)
except sr.UnknownValueError:
    print("Speech could not be recognized.")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))