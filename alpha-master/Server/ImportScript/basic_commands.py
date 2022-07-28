from unittest import result
from Core.command import *; 
from Modules import weather_module; 
import math; 

def _speak_command_check_weather(spoken_sentence:str, command: VoiceCommand, args: list, **extra):#spoken_sentence:str, command: VoiceCommand, args: list): 
    return (Result.SUCCESS, weather_module.get_irvine_weather()); 

def _speak_command_return(spoken_sentence:str, command: VoiceCommand, args: list, **extra):
    return (Result.EXIT, ""); 

def _query_command_weather(spoken_sentence:str, command: VoiceCommand, args: list, **extra):
    return (Result.SUCCESS, weather_module.get_weather(args[0]));   

def power_two_numbers(spoken_sentence:str, command: VoiceCommand, args: list, **extra):
    first_number = int(args[0]); 
    second_number = int(args[1]); 

    result = math.pow(first_number, second_number); 
    return_sentence = f"The {first_number} to the power of {second_number} is {result}"; 
    return (Result.SUCCESS, return_sentence);  

def add_two_numbers(spoken_sentence:str, command: VoiceCommand, args: list, **extra): 
    first_number = int(args[0]); 
    second_number = int(args[1]); 

    result = first_number + second_number; 
    return_sentence = f"{first_number} plus {second_number} is {result}"; 
    return (Result.SUCCESS, return_sentence); 
