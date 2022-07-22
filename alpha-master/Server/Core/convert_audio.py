from os import path; 
import os; 
from pydub import AudioSegment; 
import sys; 

audioname = sys.argv[1];   
print(audioname);
export_path = audioname[:audioname.rindex('.')] + ".wav";  
sound = AudioSegment.from_mp3(audioname);  
sound.export(export_path, format = "wav"); 

from os import path;
import os;
from pydub import AudioSegment;
import subprocess;

def convert_export_as_wave(filename): 
    file_path = os.getcwd() + '\\' + filename; 
    print('importing from', file_path); 
    export_path = os.getcwd() + '\\' + filename[:filename.rindex('.')] + ".wav"; 
    print('exporting the file to', export_path); 
    sound = AudioSegment.from_mp3(file_path);  
    sound.export(export_path, format = "wav"); 
    #return sound;


def export_as_wave(filename): 
    print('importing from', filename); 
    export_path = filename[:filename.rindex('.')] + ".wav"; 
    print('exporting the file to', export_path); 
    subprocess.call(['ffmpeg', '-i', filename, export_path], shell=True); 