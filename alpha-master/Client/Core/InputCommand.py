from Core.client_system import *; 
from Core import utility as util; 
import pandas as pd; 

COMMANDS_PATH = util.RESOURCE_DIR + "/InputCommandList.csv"

class Command:
    def __init__(self, keyword, function, description):
        self.keyword = keyword; 
        self.function = function; 
        self.description = description; 

    def __str__(self):
        return f'\t{self.keyword}\t\t{self.description}';  

class InputCommand(object):
    def __init__(self):
        self.commands = dict(); 

    def add(self, key:str, value):
        if key in self.commands.keys(): 
            print_warning("Input Command", "Key Already Exists, but this should be checked! Ignoring..."); 
            return; 
        self.commands[key] = value; 

    def set_function(self, keywords, function):
        keys = keywords.split(','); 
        for key in keys:
            key = key.strip(); 
            self.commands[key].function = function; 

    def run(self, sentence:str, *args):
        sentence = sentence.strip(); 
        if not sentence.startswith("/"): return; 
        for key in self.commands.keys():
            if sentence.startswith("/" + key):
                return self.commands[key].function(*args);  
 
        println("Input Command", "The given command does not exist. Please type \"/help\" for commands."); 
        return;  
     
    #### CALLED FUNC ####

    def list_commands(self, *args):
        print("\t----- COMMANDS ------"); 
        for command in self.commands.values():
            print(str(command));  
        print("\t----- COMMANDS ------"); 

    def stop(self, *args):
        raise Exception("You chose to exit violently."); 

    @staticmethod
    def import_commands():  
        commands = InputCommand();  
        file = open(COMMANDS_PATH, "r"); 
        df = pd.read_csv(file, sep=',');  
        for row in df.iterrows(): 
            row = row[1];  
            
            input_keyword:str = util.parse_dataframe_row(str, row, "command input").strip(); 
            function_name:str = util.parse_dataframe_row(str, row, "function name").strip(); 
            source:str = util.parse_dataframe_row(str, row, "source").strip(); 
            description:str = util.parse_dataframe_row(str, row, "description").strip(); 
            
            input_keywords = input_keyword.split(","); 
            for keyword in input_keywords:
                keyword = keyword.strip(); 

                if "client" in source.lower():
                    command = Command(keyword, None, description); 
                    commands.add(keyword, command);  
                else:  
                    print_warning("Input Command", "Not yet implemented. Skipping..."); 
                    break; 
                    #to be implemented 
        println("Input Command", "Import Successful."); 
        return commands; 


