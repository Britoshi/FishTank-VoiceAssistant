from xml.dom import NotFoundErr
import speech_recognition;  
import socket;
import select;
import time;
import pickle; 
from enum import IntEnum;
from Modules import utility as util; 
from Modules import text_to_speech;
from AudioPlayer import audio_player;
from os import system;   
import sys;

def callback(recognizer, audio):
    try:
        print("Google Speech Recognition thinks you said " + recognizer.recognize_google(audio))
    except speech_recognition.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except speech_recognition.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


RECOGNIZER = speech_recognition.Recognizer(); 
MICROPHONE = speech_recognition.Microphone();  

with MICROPHONE as source:
    RECOGNIZER.adjust_for_ambient_noise(source); 

listener = RECOGNIZER.listen_in_background(MICROPHONE, callback); 

while True:
    pass; 