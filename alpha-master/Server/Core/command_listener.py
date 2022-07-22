from dataclasses import replace
from sre_constants import SUCCESS
from tokenize import Token
from setuptools import Command
import speech_recognition;   
from Modules import weather_module; 
from enum import Enum;
from enum import IntEnum; 
from Modules import resource_importer as resources; 

class Result(IntEnum): 
    SUCCESS = 1     
    FAIL = 2        
    CONTINUE = 3    
    EXIT = 4        
    TIMEOUT = 5     

class CommandType(IntEnum):
    STRICT = 1; #"STRICT" 
    FREE = 0; #"FREE" 
    
    def __str__(self):
        if self == CommandType.STRICT:
            return "Strict"; 
        elif self == CommandType.FREE:
            return "Free";  

def parse_command_type(string:str):
    string = string.upper(); 
    print(string); 
    if(string == "STRICT"):
        return CommandType.STRICT; 
    elif(string == "FREE"):
        return CommandType.FREE; 

class VoiceCommand:
    def __init__(self, priority: int, name: str, trigger_word, function, type: CommandType, query_list: list = [], script = None):
        self.priority = priority; 
        self.name = name; 
        self.trigger_word = trigger_word; 
        self.function = function; 
        self.type:CommandType = type; 
        
        #most likely optional
        self.query_list = query_list; 
        self.queryable =  len(query_list) != 0; 
        self._next_word = ""; 
        self.script = script; 
    
    def check_strict_sentence(self, spoken_sentence:str):
        if(self.type != CommandType.STRICT):
            raise Exception("A strict search is being done for a free type!!!"); 
        
        sentence = spoken_sentence.replace(" ", '');  
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
        command_index = spoken_sentence.index(self.trigger_word) + len(self.trigger_word); 
        sentence = " " + spoken_sentence[command_index:].strip(); 
        m_sentence = sentence + ""; 

        if len(sentence) <= 1: #not long enough, probably not the right command.
            print("failed from not long enough sentence")
            return (self.QueryResult.FAIL, None); 

        if not self.queryable:
            print("ERROR: Don't run this when the command is not built for it???"); 
            return (self.QueryResult.ERROR, None);  

        queried_words = list(); 
        keywords = list();  
        [queried_words.append("") for _ in self.query_list]; #add how many ever you need 
        
        # now you have to iterate through what's in between.
        for i in range(len(self.query_list)): 
            query: list = self.query_list[i]; 
            if(len(query) == 0):
                print("ERROR: EMPTY QUERY???"); 
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
                print("failed from finding nothing")
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
                print('failed from the quried words being empty')
                return (self.QueryResult.FAIL, None);   
                
        return (self.QueryResult.SUCCESS, queried_words); 


    def __lt__(self, other): 
        condition1 = self.trigger_word < other.trigger_word; 
        condition2 = self.priority < other.priority; 
        condition3 = int(self.type) < int(self.type); 
        return condition1 and condition2 and condition3; 
        
    def __le__(self, other):
        condition1 = self.trigger_word <= other.trigger_word; 
        condition2 = self.priority <= other.priority; 
        condition3 = int(self.type) <= int(self.type); 
        return condition1 and condition2 and condition3; 

    def __eq__(self, other):
        condition1 = self.trigger_word == other.trigger_word; 
        condition2 = self.priority == other.priority; 
        condition3 = int(self.type) == int(self.type); 
        return condition1 and condition2 and condition3; 

    def __ne__(self, other):
        condition1 = self.trigger_word != other.trigger_word; 
        condition2 = self.priority != other.priority; 
        condition3 = int(self.type) != int(self.type); 
        return condition1 and condition2 and condition3; 

    def __gt__(self, other):
        condition1 = self.trigger_word > other.trigger_word; 
        condition2 = self.priority > other.priority; 
        condition3 = int(self.type) > int(self.type); 
        return condition1 and condition2 and condition3; 

    def __ge__(self, other):
        condition1 = self.trigger_word >= other.trigger_word; 
        condition2 = self.priority >= other.priority; 
        condition3 = int(self.type) >= int(self.type); 
        return condition1 and condition2 and condition3;  
        
    def __str__(self):
        return f"Prio: {self.priority},\t Name/Type: {self.name},\t Command Type: {self.type},\t Trigger Word: {self.trigger_word},\t Query List: {self.query_list}."

# what is the wheather in irvine in us
#0 
#1
class Response:
    def __init__(self, result, response_text, spoken_sentence, trigger_command):
        self.result = result; 
        self.response_text = response_text; 
        self.spoken_sentence = spoken_sentence; 
        self.trigger_command = trigger_command; 

#################################################
#               Command Functions               #
#################################################

def _speak_command_check_weather(spoken_sentence, command): 
    return (Result.SUCCESS, weather_module.get_irvine_weather()); 

def _speak_command_return(spoken_sentence, command):
    return (Result.EXIT, ""); 

def _query_command_weather(spoken_sentence, command, args):
    return (Result.SUCCESS, weather_module.get_weather(args[0]));  

#################################################
#          NETWORK HANDLING SOCKETS             #
################################################# 
 
import socket;   

def get_token(token_string:str): 
    return resources.get_token(token_string); 

def request_response_from_clients(sock:socket.socket, timeout):
    sentence = get_token("REQUEST_SENTENCE") + "|TIMEOUT=" + str(timeout); 
    encodedMessage = bytes(sentence, 'utf-8'); 
    sock.sendall(encodedMessage); 

    print("receiving packets...", end = " "); 
    data = sock.recv(1024 * 4);         
    spoken_sentence = data.decode("utf-8");  

    if get_token("TIMEOUT") in spoken_sentence:
        return None;  
    
    print(" done");   
    return spoken_sentence;   

#################################################
#####           RESPONSE GETTER             #####
#################################################

def get_response(spoken_sentence, voice_commands:list):
  
    potential_commands = [voice_command for voice_command in reversed(voice_commands) if voice_command.trigger_word in spoken_sentence]; 

    for voice_command in potential_commands: 
        voice_command: VoiceCommand = voice_command; 

        if voice_command.queryable: 
            query_result, queried_words = voice_command.query_for_words(spoken_sentence); 

            if query_result == VoiceCommand.QueryResult.SUCCESS:
                
                command_result, response_text = voice_command.function(spoken_sentence, voice_command, queried_words); 

                #method fail check   
                if command_result == Result.FAIL:
                    continue;  

                return Response(command_result, response_text, spoken_sentence, voice_command.trigger_word);  

            elif query_result == VoiceCommand.QueryResult.FAIL:
                continue; 
            else:
                raise Exception("Something went terribly wrong in Query Commands", query_result); 
        #Non Queryable
        else: 
            if voice_command.type == CommandType.STRICT:
                strict_check_result = voice_command.check_strict_sentence(spoken_sentence); 
                if strict_check_result == Result.FAIL:
                    continue;    
                
            command_result, response_text = voice_command.function(spoken_sentence, voice_command); 
            if command_result == Result.FAIL:
                continue;  

            return Response(command_result, response_text, spoken_sentence, voice_command.trigger_word); 
 
    return Response(Result.FAIL, "Sorry, I don't understand.", spoken_sentence, "N/A"); 
 
def request_sentence(socket, timeout): 
    return request_response_from_clients(socket, timeout); 


def voice_recognition_detect(socket, voice_commands:list, timeout = 5): 
    
    spoken_sentence = request_sentence(socket, timeout);   

    if spoken_sentence == None:
        return Response(Result.TIMEOUT, "Timed Out", spoken_sentence, "N/A"); 
    
    return get_response(spoken_sentence, voice_commands);  

        
def voice_recognition_detect_loop(socket, voice_commands:list, recognizer: speech_recognition.Recognizer, keywords: list, timeout, exit_commands = ["stop"]):
    
    def on_recognition_failure(spoken_sentence): 
        return voice_recognition_detect_loop(socket, voice_commands, recognizer, keywords, timeout, exit_commands = exit_commands); 
    
    spoken_sentence = request_sentence(socket, timeout); 
    
    if spoken_sentence == None:
        return on_recognition_failure(spoken_sentence);  

    # this is used for exiting only 
    if(any(exit_command in spoken_sentence for exit_command in exit_commands)): 
        return Response(Result.EXIT, None, "Exited Gracefully", None);  
    
    # check if keywords are in

    detected_word = None; 

    for keyword in keywords:
        if keyword in spoken_sentence:
            detected_word = keyword;  

    if(detected_word != None):  

        keyword_index = spoken_sentence.rindex(detected_word); 
        length = len(spoken_sentence); 
        length_to_word = len(spoken_sentence[:keyword_index + len(detected_word)]); 
        diff = length - length_to_word; 

        if(diff >= 3):
            #this means there's more than 3 extra characters, then try to get more command
            continued_words = spoken_sentence[length_to_word:].strip(); 
            response = get_response(continued_words, voice_commands); 
            
            if response.result == Result.SUCCESS:
                response.result = Result.CONTINUE; 
                return response; 

        return Response(Result.SUCCESS, None, spoken_sentence, None); 
    else:
        return on_recognition_failure(spoken_sentence); 
