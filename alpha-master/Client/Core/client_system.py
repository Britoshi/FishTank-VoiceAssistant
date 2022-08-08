def println(*values:object):
    print("CLIENT:", *values);  

def println(source:str, *values:object):
    print("CLIENT @", source, "->", *values);  

def println(source:str, *values:object, end = None):
    print("CLIENT @", source, "->", *values, end=end);  
 
def print_warning(source:str, *values:object):
    print("CLIENT @", source, "-> Warning:\n", *values); 
 
def print_error(source:str, *values:object):
    print("CLIENT @", source, "-> Error:\n", *values); 
  
def print_fatal_error(source:str, *values:object):
    print("CLIENT @", source, "-> Fatal Error:\n", *values);  

def print_please_read(*link:str):
    print("Please Read:", link); 