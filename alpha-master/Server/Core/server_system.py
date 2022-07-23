@staticmethod
def println(*values:object):
    print("SERVER:", *values);  

def println(source:str, *values:object):
    print("SERVER @", source, "->", *values);  

def println(source:str, *values:object, end = None):
    print("SERVER @", source, "->", *values, end=end);  

@staticmethod
def print_warning(source:str, *values:object):
    print("SERVER @", source, "-> Warning:\n", *values); 

@staticmethod
def print_error(source:str, *values:object):
    print("SERVER @", source, "-> Error:\n", *values); 
 
@staticmethod
def print_fatal_error(source:str, *values:object):
    print("SERVER @", source, "-> Fatal Error:\n", *values);  

def print_please_read(*link:str):
    print("Please Read:", link); 