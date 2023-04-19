from aiohttp import BytesIOPayload
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
#sudo apt-get install ffmpeg
#pip install pydub ,pydub playback ,gtts ,io

language = "ru"
text = "Hello, my name s anton, every morning i usualy get up at seven o'clock and brush my teeth, then i have Breakfast and go to school by bus"
speech = gTTS(
    text=text,
    lang=language, 
    slow=False
)

audio_bytes = BytesIO()
speech.write_to_fp(audio_bytes)
audio_bytes.seek(0)

audio_segment = AudioSegment.from_file(audio_bytes, format="mp3")

play(audio_segment)

