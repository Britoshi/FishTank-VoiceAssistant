from calendar import month_name; 
from datetime import datetime; 
from Core.command import *;
import Core.utility as util; 

def tell_time(spoken_sentence:str, command: VoiceCommand, args: list, **extra):  
    return (1, "it is " + datetime.datetime.now().strftime("%I:%M %p"));  


def tell_calendar(spoken_sentence:str, command: VoiceCommand, args: list, **extra): 
    date = datetime.datetime.now().date();   
    return_string = date.strftime('%B %d'); 
    return (1, f"Today is {return_string}."); 

def tell_date(spoken_sentence:str, command: VoiceCommand, args: list, **extra):  
    return (1, f"Today is {datetime.datetime.now().strftime('%A')}.");  