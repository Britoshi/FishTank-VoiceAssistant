from pathlib import Path;  
from os.path import exists;  
from io import TextIOWrapper  
import requests
import pandas as pd;
from subprocess import call; 
import os, glob, sys; 
import inspect; 
import math;  
from Core.command import *;
from Core.command_listener import Response; 
from Core.server_system import *; 
import socket; 
from enum import Enum;
from enum import EnumMeta;
from os import system; 
from sys import platform; 
import Core.path as path; 

global token_dictionary; 
token_dictionary = None; 

PARENT_DIR = path.home(); 

COMMAND_FOLDER_PATH = PARENT_DIR + r'/Resources/command list import/';  
TOKEN_PATH = PARENT_DIR + r"/Resources/TOKEN.txt";  
CONFIG_PATH = PARENT_DIR + r"/properties.cfg";  

sys.path.insert(1, PARENT_DIR);  
 

######################################################################
######                      Class / Object                      ######
######################################################################

class Source(EnumMeta):
    SERVER="SERVER"; 
    CLIENT="CLIENT";  

class VariableHolder:
    def __init__(self): 
        self.stop_threads = False;   
        self.exception = None;  

class Configuration(object): 

    def __init__(self, default:bool = True):
        if default:   
            self.HOST_IP = "localhost"; 
            self.PORT = 42069; 
            self.DISCORD_TOKEN = ""; 
            self.DISCORD_CHANNEL_ID = -1;  

        else:
            self.HOST_IP = None; 
            self.PORT = None;   
            self.DISCORD_TOKEN = "";  
            self.DISCORD_CHANNEL_ID = -1; 
 
    def to_readable(self):
        text = "#FishTank Voice Assistant Configuration Version 0.1\n"; 
        text += "HOST_IP=" + self.HOST_IP + "\n"; 
        text += "PORT=" + str(self.PORT) + "\n"; 
        text += "DISCORD_TOKEN=" + self.DISCORD_TOKEN + "\n"; 
        text += "DISCORD_CHANNEL_ID=" + str(self.DISCORD_CHANNEL_ID); 
        return text; 

    @staticmethod
    def __print_github():
        print_please_read(r"https://github.com/Britoshi/FishTank-VoiceAssistant/tree/main/alpha-master/Client#%EF%B8%8F-configuration"); 
 
    @classmethod
    def load_config(cls):
        """ 
        Parses the configuration file and return it as usable dictionary object.  

        If the configuration file does not exist, the configuration file is automatically generated.

        Returns
        -------
        Configuration
            The Configuration parsed from the existing file. 
        """ 
        if not file_exists(CONFIG_PATH): 
            println("Configuration", "No configuration file found, generating one at: " + CONFIG_PATH); 
            return Configuration.generate_config(); 

        configuration = Configuration(default = False);  
        duplicate_detector = list(); 

        file = open(CONFIG_PATH, "r"); 
        for line in file.readlines():
            #Checks
            if len(line.strip()) == 0: continue; 
            if line[0] == "#" : continue; 
            if "=" not in line: 
                print_warning("Configuration", "Incorrect formatting in configuration file. Ignoring and continuing."); 
                cls.__print_github(); 
                continue; 
            #If nothing's wrong
            tokens = line.split("="); 

            config_name = tokens[0].strip(); 
            config_content = tokens[1].strip();  
            
            if config_name == "HOST_IP":
                configuration.HOST_IP = config_content; 
            elif config_name == "PORT":
                try:
                    configuration.PORT = int(config_content); 
                except:
                    print_error("Configuration", "PORT MUST BE A NUMBER GREATER THAN 1024 AND MUST NOT CONTAIN ANY ALPHABETS! LOADING DEFAULT CONFIGURATION"); 
                    return error_reroute(); 
            elif config_name == "DISCORD_TOKEN":
                configuration.DISCORD_TOKEN = config_content; 
            elif config_name == "DISCORD_CHANNEL_ID":
                try:
                    configuration.DISCORD_CHANNEL_ID = int(config_content); 
                except:
                    print_error("Configuration", "DISCORD CHANNEL ID MUST BE ALL INTEGERS!"); 
                    configuration.DISCORD_CHANNEL_ID = -1; 
            else:
                print_warning("Configuration", f"Given Config name of '{config_name}' does not match. Ignoring and continuing"); 
                cls.__print_github(); 
                continue; 

            if config_name in duplicate_detector:
                print_warning("Configuration", f"The given config name '{config_name}' is a duplicate, please make sure there's only one."); 
                continue; 

            duplicate_detector.append(config_name);  
            #End of readline 
        
        def error_reroute(item):
            print_error("Configuration", f"{item} NOT FOUND IN THE CONFIGURATION! LOADING DEFAULT CONFIGURATION"); 
            return Configuration(); 

        if configuration.HOST_IP == None: return error_reroute("HOST_IP"); 
        elif configuration.PORT == None: return error_reroute("PORT"); 

        println("Configuration", "Configuration Importation Successful."); 
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


def __download_file_from_google_drive(destination):
    URL = "https://raw.githubusercontent.com/Britoshi/FishTank-VoiceAssistant/alpha-0.2/resources/TOKEN%20MASTER.txt"; 
    session = requests.Session(); 
    response = session.get(URL, stream = True)
    token = __get_confirm_token(response); 
    if token:
        params = { 'confirm' : token }
        response = session.get(URL, params = params, stream = True) 
    __save_response_content(response, destination)    

def __get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value; 
    return None

def __save_response_content(response, destination):
    CHUNK_SIZE = 32768; 
    data = b"";  
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk); 
                data += chunk;  
    global token_dictionary; 
    get_token_dictionary();     

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

def initialize_server():   
    config = Configuration.load_config();    
    # instantiate a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); 
    println("NETWORK",'Socket Instantiated'); 
    sock.bind((config.HOST_IP, config.PORT)); 
    sock.listen(); 
    println("NETWORK",'Socket Now Listening'); 
    conn, addr = sock.accept(); #wait
    println("NETWORK",'Socket Accepted, Got Connection Object'); 
    return (config, sock, conn, addr);  

def update_token():  
    println("Utility","THIS FUNCTION IS DEPRECATED AND WILL BE REMOVED, PLEASE DO NOT USE. THIS WILL SKIP!"); 
    return; 
    destination = TOKEN_PATH;   
    return __download_file_from_google_drive(destination);   

def parse_packet_message(message:str):
    tokens = message.split("|"); 
    #Header
    header = tokens[0];  
    #Route
    routes = tokens[1].split(">>");   
    source = routes[0]; 
    destination = routes[1];  
    #Body
    body = tokens[2];  
    tags = ""; 
    args = None; 

    body_tag_check = body.split(":"); 
    if len(body_tag_check) > 1: 
        tags = body_tag_check[0];  
        body = body_tag_check[1]; 
    
    if "*ARGS" in tags:
        args = tokens[3:];  

    return (header, source, destination, tags, body, args);  

def __format_token(source:Source, destination:Source):
    return f"{get_token_raw('KEY_TOKEN')}|{str(source)}>>{str(destination)}"; 

def get_token_raw(token_string:str):
    return get_token_dictionary()[token_string];  

def get_token(token_string:str, source:Source, destination:Source): 
    return __format_token(source, destination) + "|" + get_token_dictionary()[token_string]; 

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

def start_python_script(path): 
    command = ""; 
    python_name = "py"; 
    if platform == "linux" or platform == "linux2": 
        python_name = "python3";   
    elif platform == "darwin":
        raise Exception("MAC OS IS NOT CURRENTLY SUPPORTED")
    elif platform == "win32":
        python_name = "py";  

    call(python_name + " " + path, shell=True); 


def raise_error(e:Exception, message:str): 
    crash_log_folder = path.home("crash_logs"); 
    time = get_datetime(); 
    crash_log_dir = crash_log_folder + "/CRASH_LOG_" + time + LOG_EXTENSION; 

    path.mkdir_on_null(crash_log_folder); 
    crash_log_file = open(crash_log_dir, "w"); 

    file = get_current_log(type = 'r');  
    current_log = file.read(); 
    file.close();  
    crash_log_file.write(current_log);   
    
    print_log("\n\n\n\n***** An error has occurred. Crash Log will be generated. *****", file = crash_log_file); 
    print_log("*****", message, "*****", file = crash_log_file); 
    print_log("***** Exception: ", e, "*****\n\n", file = crash_log_file);  
    print_log("***** RESTARTING *****\n\n\n\n", file = crash_log_file); 

    file.close();  
    crash_log_file.close(); 

    raise e;  



#######################################################
######              CANVAS UPDATE                ######
#######################################################

##THIS GOES IN UTIL. 

def __get_cached_file(filename): 
    cache_folder_name = 'Cache'; 
    cache_folder_dir = path.resources(cache_folder_name); 
    if path.mkdir_on_null(cache_folder_dir):
        println("System", "Cache folder not found. Generating..."); 
        return None; 

    cache_files = path.listdir(cache_folder_dir); 
    for cache_file in cache_files:  
        #remove old cached files
        if cache_file <= get_past_date(5): 
            path.remove(path.resources(cache_folder_name, cache_file)); 
            continue; 
        if filename in cache_file:
            println("System", "Found a cached file. Using cached file: " + cache_file); 
            return open(path.resources(cache_folder_name, cache_file), 'rb'); 
    return None; 
     

def __cache_file(filename, filedata, type = "wb"):
    cache_folder_name = 'Cache'; 
    cache_folder_dir = path.resources(cache_folder_name); 
    if path.mkdir_on_null(cache_folder_dir): 
        println("System", "Cache folder not found. Generating..."); 
    
    cache_name = get_date() + "_" + filename + ".temp"; 
    file = open(path.resources(cache_folder_name, cache_name), "wb"); 
    file.write(filedata); 
    file.close(); 
    return open(path.resources(cache_folder_name, cache_name), type); 
    
    
#make sure to close it lol.
def get_file(filename, url:str, type):
    #filename = url[url.rindex("/") + 1:]; 

    cached_file = __get_cached_file(filename); 
    #If there is a cached file of it, just return cached file.
    if cached_file != None: return cached_file;  

    #now make a request to the url.
    response = requests.get(url, allow_redirects=True); 
    if response.ok:
        return __cache_file(filename, response.content, type = type);  
    print_warning("System", "The requested URL was either bad or the request was denied. Code: " + response.status_code); 
    return None;  

def check_null(*objs):
    try:
        for obj in objs:
            if obj == None: return True; 
    except:
        return True; 
    return False; 

def localize_items(*items):
    '''
    returns in a format of "_, _, and _"
    '''
    iter = [];  
    for titem in items:
        if type(titem) == list or type(titem) == tuple:
            [iter.append(ttitem) for ttitem in titem]; 
            continue; 
        iter.append(titem); 

    return_string = str(); 
    length = len(iter); 

    
    if length == 1:
        return str(iter[0]); 
    elif length == 2:
        return str(iter[0]) + ' and ' + str(iter[1]); 

    for i in range(length):
        item = iter[i];   

        if i + 1 == len(iter): return_string += "and " + str(item); 
        else: return_string += str(item) + ", "; 
    return return_string;  

def datetime_to_readable(time):
    return time.strftime("%I:%M %p"); 