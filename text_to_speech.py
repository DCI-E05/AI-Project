import os
import json
import subprocess
from pprint import pprint
from elevenlabs import generate, play, set_api_key, voices

set_api_key("7349ffe83ba56a8b09f784e1173d53a5")

voices_map = {
        "Crackhead": "Crackhead",
        "Employee-kaufland": "Domi",
        "Markus": "Markus",
        "Crusader": "Antoni",
        "Mike Tyson": "Tyson",
        "Batman": "Adam",
        "Batman Rogue": "Antoni",
        "Eminem": "Adam"
}

for voice in voices():
    if voice.name == "Crackhead":
        voices_map["Crackhead"] = voice
    if voice.name == "Markus": 
        voices_map["Markus"] = voice
    if voice.name == "Tyson":
        voices_map["Mike Tyson"] = voice


# set_api_key("408b5dac61855f58fbadd1e24910da6e") # Abdullah

class TextToSpeech:
    def __init__(self, voice, language="en", slow=False):
        self.language = language
        self.slow = slow
        self.voice = voices_map.get(voice, None)
        # self.voice = voice
        self.proc = None

    def set_voice(self, new_voice):
        self.voice = voices_map.get(new_voice, None)
        # self.voice = new_voice

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
        audio = generate(text=text, voice=self.voice, api_key="7349ffe83ba56a8b09f784e1173d53a5")
        self.play(audio)

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait()


if __name__ == "__main__":
    voice_role = voices_map["Crusader"]
    tts = TextToSpeech(voice=voice_role)
    tts.speak("Hello, my dear, how are you?")