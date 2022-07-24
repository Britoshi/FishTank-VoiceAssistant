from Core.command import *; 
from Modules import weather_module; 

def _speak_command_check_weather(spoken_sentence:str, command: VoiceCommand, args: list): 
    return (Result.SUCCESS, weather_module.get_irvine_weather()); 

def _speak_command_return(spoken_sentence:str, command: VoiceCommand, args: list):
    return (Result.EXIT, ""); 

def _query_command_weather(spoken_sentence:str, command: VoiceCommand, args: list):
    return (Result.SUCCESS, weather_module.get_weather(args[0]));  

from Core.command import *
import math

def power_two_numbers(spoken_sentence:str, command: VoiceCommand, args: list):
    first_number = int(args[0]); 
    second_number = int(args[1]); 

    result = math.pow(first_number, second_number); 
    return_sentence = f"The power of {first_number} to the {second_number} is {result}"; 
    return (Result.SUCCESS, return_sentence);  


