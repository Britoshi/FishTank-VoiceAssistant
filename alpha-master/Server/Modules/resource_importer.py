from cmath import nan
from io import TextIOWrapper 
import requests
import pandas as pd;
from pathlib import Path;  

import os, glob, sys; 
import inspect
import math; 
import importlib;  

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir); 

from Core import command_listener; 

parent_dir = str(Path("__init__.py").parent.absolute());   

COMMAND_FOLDER_PATH = parent_dir + '\\Resources\\command list import\\'; 

def parse_commands() -> list:
    
    commands = list();  
    script_dictionary = {}; 

    os.chdir(COMMAND_FOLDER_PATH)
    for file in glob.glob("*.csv"):
        print(file) 
        df = pd.read_csv(file, sep=',');   

        try:
            for row in df.iterrows():

                row = row[1];  
                priority:int = int(row["priority"]); 
                name:str = row["type"]; 

                trigger_word_string:str = row["trigger words"]; 
                trigger_words = trigger_word_string.split(','); 

                command_type = command_listener.parse_command_type(row["command type"]); 

                query_list = list();    

                query_list_string = row["query list"];              
                if type(query_list_string) != float:
                    query_separate = query_list_string.split("|");  
                    for separated in query_separate: 
                        query_list.append(list(separated.split(',')));  


                function_string:str = row["function"]; 
                script_name = row["import script name"]; 
                function_root = command_listener; 
                script_object = None;

                if type(script_name) != float:
                    if script_name not in script_dictionary.keys():
                        path = "ImportScript." + script_name; 
                        print(path); 
                        script_dictionary[script_name] = importlib.import_module(path); 
                        script_object =script_dictionary[script_name]; 
                        
                    function_root = script_dictionary[script_name];  

                function = getattr(function_root, function_string); 

                #Warning Check 1
                if command_type == command_listener.CommandType.STRICT and len(query_list) != 0:
                    print("WARNING: Query Command should not have a Command Type of STRICT. Changing it to FREE."); 
                    command_type = command_listener.CommandType.FREE; 

                for trigger_word in trigger_words: 
                    trigger_word = trigger_word.strip(); 
                    command = command_listener.VoiceCommand(priority=priority, name=name, trigger_word=trigger_word, function=function, type=command_type,query_list=query_list, script= script_object);  
                    commands.append(command); 
        except:
            raise Exception(f"You messed up with the formating with {file}, go fix it and rerun the server script."); 
            
    commands.sort(); 
    return commands;  

global token_dictionary; 
token_dictionary = None; 

def _download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = _get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    _save_response_content(response, destination)    

def _get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def _save_response_content(response, destination):
    CHUNK_SIZE = 32768

    data = b""; 

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk); 
                data += chunk; 

    global token_dictionary; 
    get_token_dictionary();  
    print(token_dictionary); 

TOKEN_PATH = parent_dir + "\\Resources\\TOKEN.txt";  

def update_token(): 
    file_id = '18uWZCUYY6DGAT1wlaq2QjNbCbOQ4EqPt'
    destination = TOKEN_PATH;  
    return _download_file_from_google_drive(file_id, destination); 

def get_token(token_string:str):
    token_dic = get_token_dictionary();  
    if token_string == "KEY_TOKEN":
        return token_dic["KEY_TOKEN"]; 
    return token_dic["KEY_TOKEN"] + "|" + token_dic[token_string]; 

def get_token_dictionary(refresh = False) -> dict:
    global token_dictionary;  

    if(refresh == True):
        update_token(); 
 
    if(token_dictionary == None): 
        dictionary = dict(); 
        file = TextIOWrapper; 
        try:
            file = open(TOKEN_PATH, 'r'); 
        except FileNotFoundError:
            return get_token_dictionary(refresh=True); 

        for line in file.readlines():
            if len(line) <= 1:
                continue;   
                            
            if line[0] == "#":
                continue; 
                
            token = line.split(','); 
            dictionary[token[0]] = token[1].replace("\n", '').strip();  
        token_dictionary = dictionary; 
        return token_dictionary; 
    else:
        return token_dictionary;   