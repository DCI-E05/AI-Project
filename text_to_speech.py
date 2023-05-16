import os
import json
import subprocess
from elevenlabs import generate, play, set_api_key, voices

voices_map = {
        #"Crackhead": "crackhead",
        "Employee-kaufland": "Domi",
        #"Markus": "Markus",
        "Crusader": "Antoni",
        "Mike Tyson": "Adam",
        "Batman": "Adam",
        "Batman Rogue": "Antoni",
        "Eminem": "Adam"
}

set_api_key("408b5dac61855f58fbadd1e24910da6e")

class TextToSpeech:
    def __init__(self, voice, language="en", slow=False):
        self.language = language
        self.slow = slow
        self.voice = voices_map.get(voice, None)
        self.proc = None

    def set_voice(self, new_voice):
        self.voice = voices_map.get(new_voice, None)

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
    lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum varius consequat libero, a porta sapien pharetra quis. Mauris ante turpis, pulvinar condimentum tellus id, vulputate ullamcorper dui. Nulla nunc tortor, scelerisque non ex id, placerat viverra tortor. Nam volutpat nibh in est mollis, sed volutpat sapien auctor. Vivamus interdum augue id diam venenatis, vel sagittis odio semper. Proin tellus diam, congue at ipsum eget, aliquet mollis felis. Morbi tempus mi felis, a feugiat orci ultrices eu.

Donec eget quam commodo nisi placerat tempor. Nunc vitae eleifend risus. Ut consequat libero purus, et sagittis mi fringilla a. Duis sed posuere ipsum. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Duis consequat tempor orci a aliquam. Fusce lectus mauris, consequat tempor pretium id, pretium a eros. Nullam vulputate sed lorem venenatis posuere. Sed eget finibus diam. Nulla facilisi. Mauris at rutrum arcu, eget dictum nisi."""
    voice_role = voices_map["crusader"]
    tts = TextToSpeech(voice=voice_role)
    tts.speak(lorem)