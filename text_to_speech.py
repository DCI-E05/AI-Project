import os
import json
import subprocess
from elevenlabs import generate, play, set_api_key, voices

set_api_key("408b5dac61855f58fbadd1e24910da6e")

class TextToSpeech:
    def __init__(self, voice, language="en", slow=False):
        self.language = language
        self.slow = slow
        self.voice = voice
        self.proc = None

    def play(self, audio: bytes, notebook: bool = False) -> None:
        if notebook:
            from IPython.display import Audio, display
            display(Audio(audio, rate=44100, autoplay=True))
        else:
            args = ["ffplay", "-autoexit", "-nodisp", "-i", "-"]
            self.proc = subprocess.Popen(
                args=args,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.proc.communicate(input=audio)

    def speak(self, text):
        audio = generate(text=text, voice=self.voice)
        self.play(audio)

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait()


if __name__ == "__main__":
    voices_map = {
        #"crackhead": "crackhead",
        "employee-kaufland": "Domi",
        #"Markus": "Markus",
        "crusader": "Antoni",
        "mike-tyson": "Adam",
        "batman": "Adam",
        "batman-rogue": "Antoni",
        "eminem": "Adam"
    }

    bot = input(
    """choose the role of GPT:
employee-kaufland
crusader
mike-tyson
batman
eminem
""") 
    voice_role = voices_map[bot]
    tts = TextToSpeech(voice=voice_role)
    tts.speak("Hello, I am your text to speech assistant.")