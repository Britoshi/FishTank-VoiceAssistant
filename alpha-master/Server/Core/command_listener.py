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

class CommandListener:
    def __init__(self, socket:socket.socket, voice_commands:VoiceCommands):
        self.loop_timeout = 30; 
        self.socket = socket; 
        self.voice_commands = voice_commands; 

    def get_command_list(self):
        return self.voice_commands.voice_commands; 

    def request_response_from_clients(self, timeout = None):
        if timeout == None:
            timeout == self.loop_timeout; 

        sentence = util.get_token("REQUEST_SENTENCE", util.Source.SERVER, util.Source.CLIENT) + "|TIMEOUT=" + str(timeout); 
        encodedMessage = bytes(sentence, 'utf-8'); 
        self.socket.sendall(encodedMessage);  

#################################################
#####           RESPONSE GETTER             #####
#################################################

    def get_response(self, spoken_sentence):
     
        potential_commands = [voice_command for voice_command in reversed(self.get_command_list()) if voice_command.trigger_word in spoken_sentence]; 

        for voice_command in potential_commands: 
            voice_command: VoiceCommand = voice_command; 

            if voice_command.queryable: 
                query_result, queried_words = voice_command.query_for_words(spoken_sentence); 

                if query_result == VoiceCommand.QueryResult.SUCCESS:
                    
                    command_result, response_text = voice_command.function(spoken_sentence, voice_command, queried_words, socket=self.socket); 

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
                    
                command_result, response_text = voice_command.function(spoken_sentence, voice_command, [], socket=self.socket); 
                if command_result == Result.FAIL:
                    continue;  

                return Response(command_result, response_text, spoken_sentence, voice_command.trigger_word); 
    
        return Response(Result.FAIL, "Sorry, I don't understand.", spoken_sentence, "N/A");  

    def on_receive_spoken_sentence(self, spoken_sentence): 
        if spoken_sentence == None:
            return Response(Result.TIMEOUT, "Timed Out", spoken_sentence, "N/A"); 
        
        return self.get_response(spoken_sentence);  
 
        
    def on_receive_spoken_sentence_loop(self, spoken_sentence, keywords: list, exit_commands = ["stop"]): 

        def on_recognition_failure(): 
            return Response(Result.FAIL, None, spoken_sentence, None); #self.request_response_from_clients(); 
        
        if spoken_sentence == None:
            return on_recognition_failure();  

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
                response = self.get_response(continued_words); 
                
                if response.result == Result.SUCCESS:
                    response.result = Result.CONTINUE; 
                    return response; 

            return Response(Result.SUCCESS, None, spoken_sentence, None); 
        else: return on_recognition_failure(); 


#################################################
#          NETWORK HANDLING SOCKETS             #
################################################# 
 

