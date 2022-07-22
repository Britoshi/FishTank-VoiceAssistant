
from pathlib import Path;  
import requests


path = str(Path("__init__.py").parent.absolute());  
parent_dir = path; 

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
        file = None; 
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