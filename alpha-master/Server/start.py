from time import sleep; 
from os import system; 
from sys import platform; 
import Core.utility as util;
from Core.utility import start_python_script as start; 
import os;    
import subprocess

python_name = "py"; 
if platform == "linux" or platform == "linux2": 
    python_name = "python3"; 
elif platform == "darwin":
    raise Exception("MAC OS IS NOT CURRENTLY SUPPORTED")
elif platform == "win32":
    python_name = "py"; 


file_name = "start.py";   
cur_dir = os.getcwd(); 

index = 0; 
while True:
    file_list = os.listdir(cur_dir)
    parent_dir = os.path.dirname(cur_dir)
    if file_name in file_list:
        print("Found start.py in", cur_dir); 
        break
    else:
        if cur_dir == parent_dir: #if dir is root dir
            raise Exception("Unable to find start.py?"); 
        else:
            cur_dir = parent_dir

    index += 1; 
    if index >= 5:
        raise Exception("Unable to find start.py?");  

path = python_name + " " + cur_dir + "/server_runner.py"; 

while(True): 
    try:
        start("server_runner.py"); 
    except Exception as e:
        print(e);  
    sleep(5); 
 