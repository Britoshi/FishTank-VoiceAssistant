from os.path import exists; 
from configparser import ConfigParser
from pathlib import Path
from pickle import NONE 
import requests

######################################################################
######                     CONST AND GLOBAL                     ######
######################################################################
 
global token_dictionary; 
token_dictionary = None;  

#                                                                    #
######                      CONSTANT VAR                        ######
#                                                                    #

PARENT_DIR = str(Path("__init__.py").parent.absolute()); 

TOKEN_PATH = PARENT_DIR + "\\Resources\\TOKEN.txt";  
CONFIG_PATH = PARENT_DIR + "\\properties.cfg"; 

######################################################################
######                      Class / Object                      ######
######################################################################

class Configuration(object): 
 
    def __init__(self, default:bool = True):
        if default:   
            self.HOST_IP = "192.168.1.151"; 
            self.PORT = "42069"; 
        else:
            self.HOST_IP = None; 
            self.PORT = None;   
 
    def to_readable(self):
        text = "#FishTank Voice Assistant Configuration Version 0.1\n"; 
        text += "HOST_IP=" + self.HOST_IP + "\n"; 
        text += "PORT=" + self.PORT; 
        return text; 

    @staticmethod
    def __print_github():
        print(r"Please Read: https://github.com/Britoshi/FishTank-VoiceAssistant/tree/main/alpha-master/Client#%EF%B8%8F-configuration"); 
 
    @classmethod
    def load_config(cls):
        """ 
        Parses the configuration file and return it as usuable dictionary object.  

        If the configuration file does not exist, the configuration file is automatically generated.

        Returns
        -------
        Configuration
            The Configuration parsed from the existing file. 
        """ 
        if not file_exists(CONFIG_PATH): 
            print("Configuration: No configuration file found, generating one at: " + CONFIG_PATH); 
            return Configuration.generate_config(); 

        configuration = Configuration(default = False); 

        duplicate_detector = list(); 

        file = open(CONFIG_PATH, "r"); 
        for line in file.readlines():
            #Checks
            if line[0] == "#" : continue; 
            if "=" not in line: 
                print("WARNING: Incorrect formating in confiration file. Ignoring and continuing."); 
                cls.__print_github(); 
                continue; 
            #If nothing's wrong
            tokens = line.split("="); 

            config_name = tokens[0].strip(); 
            config_content = tokens[1].strip();  
            match config_name:
                case "HOST_IP":
                    configuration.HOST_IP = config_content; 
                case "PORT":
                    configuration.PORT = config_content; 
                case _:
                    print(f"WARNING: Given Config name of '{config_name}' does not match. Ignoring and continuing"); 
                    cls.__print_github(); 
                    continue; 

            if config_name in duplicate_detector:
                print(f"WARNING: The given config name '{config_name}' is a duplicate, please make sure there's only one."); 
                continue; 

            duplicate_detector.append(config_name);  
            #End of readline 
        
        def error_reroute(item):
            print(f"ERROR: {item} NOT FOUND IN THE CONFIGURATION! LOADING DEFAULT CONFIGURATION"); 
            return Configuration(); 

        if configuration.HOST_IP == None: return error_reroute("HOST_IP"); 
        elif configuration.PORT == None: return error_reroute("PORT"); 

        print("Configuration Importation Successful."); 
        return configuration; 

    @staticmethod
    def generate_config(): 
        """
        Creates a default configuration and export the file for next time.  

        Returns
        -------
        Configuration
            The configuration containing the default values. 
        """ 
        default_configuration = Configuration();  
        file = open(CONFIG_PATH, 'w'); 
        file.write(default_configuration.to_readable()); 
        file.close();  
        return default_configuration;  

######################################################################
######                     Private Methods                      ######
###################################################################### 

def _download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download";  
    session = requests.Session() 
    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = _get_confirm_token(response) 
    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True) 
    _save_response_content(response, destination); 
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
            if chunk:
                f.write(chunk); 
                data += chunk;  
    global token_dictionary; 
    get_token_dictionary();  
    print(token_dictionary); 


######################################################################
######                      Public Methods                      ######
###################################################################### 

def file_exists(path:str) -> bool:
    """ 
    Checks if there is a file in a given parameter  

    Parameters
    ----------
    path : str
        Path to the file.

    Returns
    -------
    bool 
        Whether the file exists in a given path. 
    """ 
    return exists(path);  


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