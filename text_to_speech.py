from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
#sudo apt-get install ffmpeg
#pip install pydub ,pydub playback ,gtts ,io

def text_to_speech(text, language="en", slow=False):
    speech = gTTS(
            text=text,
            lang=language, 
            slow=slow
    )
    audio_bytes = BytesIO()
    speech.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    audio_segment = AudioSegment.from_file(audio_bytes, format="mp3")
    play(audio_segment)


text = "Hello, my name s Anton. Every morning I usually get up at seven o'clock and brush my teeth, then I have breakfast and go to school by bus."
text_to_speech(text, language="ru")



