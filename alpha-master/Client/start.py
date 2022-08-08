from time import sleep; 
from os import system; 
from sys import platform; 
from Core.utility import start_python_script as start;  

python_name = "py"; 
if platform == "linux" or platform == "linux2": 
    python_name = "python3"; 
elif platform == "darwin":
    raise Exception("MAC OS IS NOT CURRENTLY SUPPORTED")
elif platform == "win32":
    python_name = "py"; 


while(True): 
    try:
        start("client_runner.py");  
    except Exception as e:
        print(e);  
    sleep(5);  