
from enum import Enum;
from enum import IntEnum; 
import os, glob;
import pandas as pd; 
import importlib;   
from Core import utility as util;
from Core.server_system import *; 

######################################################################
#####                       VOICE COMMAND                        #####
######################################################################  

class Result(IntEnum): 
    SUCCESS = 1     
    FAIL = 2        
    CONTINUE = 3    
    EXIT = 4        
    TIMEOUT = 5     
    RELOAD = 6

class VoiceCommand:

    class Type(IntEnum):
        STRICT = 1; #"STRICT" 
        FREE = 0; #"FREE" 

    def __str__(self):
        if self == self.Type.STRICT:
            return "Strict"; 
        elif self == self.Type.FREE:
            return "Free";   
        
    @staticmethod
    def __speak_set_script(_, cmd, __):
        return (1, cmd.predetermined_speech); 

    @staticmethod
    def parse_command_type(string:str):
        string = string.upper();  
        if(string == "STRICT"):
            return VoiceCommand.Type.STRICT; 
        elif(string == "FREE"):
            return VoiceCommand.Type.FREE; 

    def __init__(self, priority: int, name: str, trigger_word, function, type: Type, query_list: list = [], script = None, predetermined_speech = None):
        self.priority = priority; 
        self.name = name; 
        self.trigger_word = trigger_word; 
        self.function = function; 
        self.type:self.Type = type; 
        
        #most likely optional
        self.query_list = query_list; 
        self.queryable =  len(query_list) != 0; 
        self._next_word = ""; 
        self.script = script; 
        self.predetermined_speech = predetermined_speech; 
    
    def check_strict_sentence(self, spoken_sentence:str):
        if(self.type != self.Type.STRICT):
            raise Exception("A strict search is being done for a free type!!!"); 
        
        sentence = spoken_sentence.strip();  
        keyword_index = sentence.rindex(self.trigger_word); 

        if(keyword_index != 0):
            return Result.FAIL; 

        length = len(sentence); 
        length_to_word = len(sentence[:keyword_index + len(self.trigger_word)]); 
        diff = length - length_to_word;  
        if(diff >= 3):
            return Result.FAIL;   
        
        return Result.SUCCESS;   

    class QueryResult:
        EMPTY = 0
        SUCCESS = 1
        FAIL = 2
        ERROR = 3
        CONTINUE = 4

    def queryable(self):
        return self.queryable; 

    def query_for_words(self, spoken_sentence:str):  

        if not self.queryable:
            print_error("Voice Command","Don't run this when the command is not built for it???"); 
            return (self.QueryResult.ERROR, None);  

        command_index = spoken_sentence.index(self.trigger_word) + len(self.trigger_word); 
        sentence = " " + spoken_sentence[command_index:].strip(); 
 
        for keyw in self.query_list[0]:
            if keyw in self.trigger_word: sentence = spoken_sentence; 

        m_sentence = sentence + ""; 

        if len(sentence) <= 1: #not long enough, probably not the right command. 
            return (self.QueryResult.FAIL, None); 


        queried_words = list(); 
        keywords = list();  
        [queried_words.append("") for _ in self.query_list]; #add how many ever you need 
        
        # now you have to iterate through what's in between.
        for i in range(len(self.query_list)): 
            query: list = self.query_list[i]; 
            if(len(query) == 0):
                print_error("Voice Command","EMPTY QUERY???"); 
                return (self.QueryResult.ERROR, None); 
 
            for j in range(len(query)): 
                word = " " + query[j] + " "; 
                if word in m_sentence: 
                    index = m_sentence.index(word); 

                    replacement = "_" * len(word);  
                    m_sentence = m_sentence.replace(word, replacement, 1);  

                    keywords.append((word, index)); 
                    break; 

            # If we found nothing, then it failed
            if len(keywords) != i + 1:
                #print("failed from finding nothing")
                return (self.QueryResult.FAIL, None);  

            #Apply the queried words
            if i != 0 and len(self.query_list) != 1: 
                last_index = keywords[i - 1][1] + len(keywords[i - 1][0]); 
                current_index = keywords[i][1];  

                queried_words[i - 1] = sentence[last_index: current_index].strip();  

            # If there's only one to go for, then just return the rest in the line.
            if len(self.query_list) == 1 or i == len(self.query_list) - 1: 
                current_index = keywords[i][1] + len(keywords[i][0]); 
                queried_words[i] = sentence[current_index:]; 
                return (self.QueryResult.SUCCESS, queried_words); 

            if queried_words[i - 1] == "" and i != 0:
                #print('failed from the quried words being empty')
                return (self.QueryResult.FAIL, None);   
                
        return (self.QueryResult.SUCCESS, queried_words); 


    def __lt__(self, other): 
        condition1 = self.trigger_word < other.trigger_word; 
        condition2 = self.priority < other.priority; 
        condition3 = int(self.type) < int(self.type); 
        condition4 = self.queryable < other.queryable; 
        return condition1 and condition2 and condition3 and condition4; 
    def __le__(self, other):
        condition1 = self.trigger_word <= other.trigger_word; 
        condition2 = self.priority <= other.priority; 
        condition3 = int(self.type) <= int(self.type); 
        condition4 = self.queryable <= other.queryable; 
        return condition1 and condition2 and condition3 and condition4; 
    def __eq__(self, other):
        condition1 = self.trigger_word == other.trigger_word; 
        condition2 = self.priority == other.priority; 
        condition3 = int(self.type) == int(self.type); 
        condition4 = self.queryable == other.queryable; 
        return condition1 and condition2 and condition3 and condition4;  
    def __ne__(self, other):
        condition1 = self.trigger_word != other.trigger_word; 
        condition2 = self.priority != other.priority; 
        condition3 = int(self.type) != int(self.type); 
        condition4 = self.queryable != other.queryable; 
        return condition1 and condition2 and condition3 and condition4; 
    def __gt__(self, other):
        condition1 = self.trigger_word > other.trigger_word; 
        condition2 = self.priority > other.priority; 
        condition3 = int(self.type) > int(self.type);  
        condition4 = self.queryable > other.queryable; 
        return condition1 and condition2 and condition3 and condition4; 
    def __ge__(self, other):
        condition1 = self.trigger_word >= other.trigger_word; 
        condition2 = self.priority >= other.priority; 
        condition3 = int(self.type) >= int(self.type); 
        condition4 = self.queryable >= other.queryable; 
        return condition1 and condition2 and condition3 and condition4; 
    def __str__(self):
        return f"Prio: {self.priority},\t Name/Type: {self.name},\t Command Type: {self.type},\t Trigger Word: {self.trigger_word},\t Query List: {self.query_list}."

    @staticmethod
    def import_commands() -> list: 
        COMMAND_FOLDER_PATH = util.COMMAND_FOLDER_PATH;  
        commands = list();  
        script_dictionary = {}; 

        os.chdir(COMMAND_FOLDER_PATH)
        for file in glob.glob("*.csv"): 
            df = pd.read_csv(file, sep=',');   
            #try:
            for row in df.iterrows(): 
                row = row[1];  
                priority:int = int(row["priority"]); 
                name:str = row["type"]; 

                trigger_word_string:str = row["trigger words"]; 
                trigger_words = trigger_word_string.split(','); 

                command_type = VoiceCommand.parse_command_type(row["command type"]); 

                query_list = list();    

                query_list_string = row["query list"];              
                if type(query_list_string) != float:
                    query_separate = query_list_string.split("|");  
                    for separated in query_separate: 
                        query_list.append(list(separated.split(',')));  


                function_string:str = row["function"];  
                function = None; 
                function_script = None; 
                script_object = None; 
                predetermined_speech = None; 

                #This checks if the command is a simple speak one sentence
                if "\"" in function_string:
                    function = VoiceCommand.__speak_set_script; 
                    predetermined_speech = function_string.replace("\"", ""); 
                else:
                    script_name = row["import script name"];  

                    if type(script_name) != float:
                        if script_name not in script_dictionary.keys():
                            path = "ImportScript." + script_name;  
                            println("Voice Command", "Adding a new python script: " + script_name); 
                            try:
                                script_dictionary[script_name] = importlib.import_module(path); 
                            except Exception as e:
                                print_error("Voice Command","There's a problem importing the script, '" + script_name + "'.")
                                print("GIVEN ERROR:", e); 
                                continue; 
                                
                            script_object = script_dictionary[script_name];   
                        function_script = script_dictionary[script_name];  
    
                    if function_script == None:
                        raise Exception("FATAL ERROR: function_script is still none, this should never ever happen.")
                        
                    function = getattr(function_script, function_string); 

                #Warning Check 1
                if command_type == VoiceCommand.Type.STRICT and len(query_list) != 0:
                    print_warning("Voice Command","Query Command should not have a Command Type of STRICT. Changing it to FREE."); 
                    command_type = VoiceCommand.Type.FREE; 

                for trigger_word in trigger_words: 
                    trigger_word = trigger_word.strip().lower(); 
                    command = VoiceCommand(priority=priority, name=name, trigger_word=trigger_word, function=function, type=command_type,query_list=query_list, script= script_object, predetermined_speech=predetermined_speech);  
                    commands.append(command); 
                        
            #except Exception as e:
            #    print_warning("Voice Command", f"You messed up with the formating with {file}. Fix it and rerun, it is skipping...");
            ##    print("Given Error Message: " + e);   
            #    continue; 

        commands.sort(); 
        println("Voice Command", "Command Importation Successful.")
        return commands;  
