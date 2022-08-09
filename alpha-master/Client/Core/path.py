import os; 
import os.path;  
from os.path import exists as path_exists; 
from os import listdir; 
from os import remove; 

PARENT_DIR = os.getcwd(); 

while True:
    file_list = listdir(PARENT_DIR); 
    up_dir = os.path.dirname(PARENT_DIR); 
    if "start.py" in file_list: break;  
    if PARENT_DIR == up_dir: #if dir is root dir
        raise Exception("Start.py cannot be found!?!?!??!?!");  
    else: PARENT_DIR = up_dir

def exists(path):
    return path_exists(path); 

def mkdir_on_null(path):
    if exists(path): return False; 
    os.mkdir(path); 
    return True; 

def make_file_on_null(path):
    if exists(path): return False; 
    open(path, "w").close();  
    return True; 

def home(*path_items):
    '''
    return path to specified path

    PARAM
    --------
    *path_items[optional] = file/folder names.
    
    EXAMPLES
    --------
    >>> home("Resources", "log")
    "root_dir/voice-assistant/Resources/log"
    >>> home("Resources", "log", "LOG_FILE.txt")
    "root_dir/voice-assistant/Resources/log/LOG_FILE.txt"
    '''
    return_path = PARENT_DIR; 
 
    if len(path_items) == 0: return PARENT_DIR; 

    for i in range(len(path_items)):
        item = path_items[i]; 
        is_last_item:bool = i + 1 == len(path_items); 

        if is_last_item:
            return return_path + f"/{item}"; 
        else: #This mean it's a directory.
            return_path += f"/{item}/"

    return return_path;  

def resources(*path_items):
    '''
    return path to specified path

    PARAM
    --------
    *path_items[optional] = file/folder names.
    
    See Also
    --------
    ``home``: does same but from the root folder.
    '''
    if len(path_items) == 0: return home("Resources"); 
    return home("Resources", *path_items); 
    