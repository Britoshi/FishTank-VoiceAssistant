from time import sleep; 
from os import system; 
from sys import platform; 

sleep(5);  

python_name = "py"; 
if platform == "linux" or platform == "linux2": 
    python_name = "python3"; 
elif platform == "darwin":
    raise Exception("MAC OS IS NOT CURRENTLY SUPPORTED")
elif platform == "win32":
    python_name = "py"; 

system(python_name + " client_runner.py"); 