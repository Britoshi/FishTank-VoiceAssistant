import pyaudio
import wave 
from pathlib import Path; 

path = str(Path("__init__.py").parent.absolute());  
parent_dir = path; 

class AudioFile:
    chunk = 1024; 

    def __init__(self, file):
        """ Init audio stream """ 
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        while data != b'':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """ Graceful shutdown """ 
        self.stream.close()
        self.p.terminate()

def Play(path): 
    audio = AudioFile(path); 
    audio.play(); 
    audio.close();  

def play_generated_sentence():
    Play(str(parent_dir) + "\\AudioPlayer\\spoken_sentence.wav"); 