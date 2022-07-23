from Core.command import *; 
from Modules import weather_module; 

def _speak_command_check_weather(spoken_sentence:str, command: VoiceCommand, args: list): 
    return (Result.SUCCESS, weather_module.get_irvine_weather()); 

def _speak_command_return(spoken_sentence:str, command: VoiceCommand, args: list):
    return (Result.EXIT, ""); 

def _query_command_weather(spoken_sentence:str, command: VoiceCommand, args: list):
    return (Result.SUCCESS, weather_module.get_weather(args[0]));  