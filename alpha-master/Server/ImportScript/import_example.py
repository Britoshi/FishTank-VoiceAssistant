from calendar import month_name
from datetime import datetime 
from Core.command import *;

def tell_time(spoken_sentence:str, command: VoiceCommand, args: list): 
    time = datetime.now(); 

    minute = time.minute; 
    hour = time.hour; 
    
    if hour > 12:
        hour -= 12; 

    if minute == 0:
        return (1, "it is " + str(hour) + " o'clock "); 

    elif minute < 10:
        return (1, "it is " + str(hour) + " o " + str(minute)); 

    return (1, "it is " + str(hour) + " " + str(minute)); 

def play_music(stn, cmd):
    cmd.script.play(); 

def tell_calendar(spoken_sentence:str, command: VoiceCommand, args: list): 
    date = datetime.now().date(); 
     

    day = str(date.day); 
    month = date.month; 

    MONTH_NAME = {
        1: "January",
        2: "Februrary",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }
    
    token = day[-1]; 
    if token == "1":
        day += "st"; 
    elif token == '2':
        day += "nd"; 
    elif token == '3':
        day += "rd"; 
    else:
        day += "th";  

    return (1, f"Today is {MONTH_NAME[month]} {day}."); 

def tell_date(spoken_sentence:str, command: VoiceCommand, args: list): 
    date = datetime.now().date();   
    
    DAY_STRING = {
        1:"Monday",
        2:"Tuesday",
        3:"Wednesday",
        4:"Thursday",
        5:"Friday", 
        6:"Saturday",
        7:"Sunday"
    }

    return (1, f"Today is {DAY_STRING[date.isoweekday()]}"); 
