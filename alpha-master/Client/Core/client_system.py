import datetime as my_datetime;  
import Core.path as path; 

##########################################################
#####                   CONSTANTS                    #####
##########################################################

LOG_TAG = "LOG";  
LOG_EXTENSION = ".log"; 
PARENT_DIR = path.home(); 
RESOURCE_DIR = path.resources(); 
LOG_DIR = path.resources("log"); 


##########################################################
#####                  PRIVATE FUNC                  #####
##########################################################

def __to_readable_time(date):
    return date.strftime("%H:%M:%S"); 

def __to_readable_date(date):
    return date.strftime("%Y_%m_%d") 

def __get_past_date(days_ago): 
    past_date = my_datetime.timedelta(days = days_ago); 
    return my_datetime.datetime.now() - past_date;  

##########################################################
#####                  PUBLIC FUNC                   #####
########################################################## 

def get_datetime():
    ''' returns the current time in a format of ``%Y_%m_%d_%H_%M_%S`` '''
    return my_datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"); 

def get_time():
    ''' returns the current time in a format of ``%H:%M:%S`` '''
    return __to_readable_time(my_datetime.datetime.now()); 

def get_date():
    ''' returns the current dates in a format of ``%Y_%m_%d`` '''
    return __to_readable_date(my_datetime.datetime.now());  

def print_log(*values, file = None):
    if file == None: 
        print(*values); 
    else: 
        print(*values); 
        print(*values, file = file); 

def println(source:str, *values:object):
    write_log(source, "", *values);  

def println(source:str, *values:object, end = None): 
    write_log(source, "", *values);  

def print_please_read(*link:str):
    print("Please Read:", link); 

def get_current_log(type = "a"):
    filename = f'{LOG_TAG}_{get_date()}{LOG_EXTENSION}'; 
    filepath = path.resources("log", filename); 
    if not path.exists(filepath): open(filepath, "w").close(); 
    return open(filepath, type);  

def write_log(source, cause, *values):  
    try:
        file = get_current_log();  
        time = get_time();  
        print_log(time + ":CLIENT @", source, f"-> {cause}", *values, file=file); 
        file.close(); 
    except Exception as e:
        print("ERROR?");  
        print(e);   

def print_warning(source:str, *values:object):
    write_log(source, "Warning:\n", *values);  
 
def print_error(source:str, *values:object):
    write_log(source, "Error:\n", *values);  

def print_fatal_error(source:str, *values:object):
    write_log(source, "Fatal Error:\n", *values);  

##########################################################
#####               INTERNAL METHODS                 #####
##########################################################

def __delete_old_logs():
    logs = path.listdir(LOG_DIR); 
    day_limit = __get_past_date(5); 
    day_limit_string = f'{LOG_TAG}_{__to_readable_date(day_limit)}{LOG_EXTENSION}'; 

    for log in logs:
        if log <= day_limit_string:
            path.remove(path.resources("log", log)); 
            println("SYSTEM", f"Old log discovered, removing:", log); 


##########################################################
#####                  INIT THINGS                   #####
##########################################################

if path.mkdir_on_null(RESOURCE_DIR):
    print(get_time() + ":SERVER @ SYSTEM: Did someone delete the resource folder???"); 

if path.mkdir_on_null(LOG_DIR):
    println("SYSTEM", "Someone deleted log folder. Generating..."); 

#Check for old logs
__delete_old_logs(); 