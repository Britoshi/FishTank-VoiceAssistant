import speech_recognition;    
from Core import utility as util; 
from Core.command import *; 
import socket;   
from Core.server_system import *; 

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

#################################################
#          NETWORK HANDLING SOCKETS             #
################################################# 
 

def get_token(token_string:str): 
    return util.get_token(token_string); 

def request_response_from_clients(sock:socket.socket, timeout):
    sentence = get_token("REQUEST_SENTENCE") + "|TIMEOUT=" + str(timeout); 
    encodedMessage = bytes(sentence, 'utf-8'); 
    sock.sendall(encodedMessage); 

    println("NETWORK", "receiving packets...", end = " "); 
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
            if voice_command.type == VoiceCommand.Type.STRICT:
                strict_check_result = voice_command.check_strict_sentence(spoken_sentence); 
                if strict_check_result == Result.FAIL:
                    continue;    
                
            command_result, response_text = voice_command.function(spoken_sentence, voice_command, []); 
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
