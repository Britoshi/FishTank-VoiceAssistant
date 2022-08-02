from calendar import isleap
from httplib2 import Response
from Core import utility as util;  
#util.update_token();  

#from Modules import text_to_speech; 
#from AudioPlayer import audio_player; 
from Core import command_listener as listener; 
from enum import Enum; 
from Core.server_system import *; 
from Core.command import *; 
from Core.custom_thread import StoppableThread as thread;
from os import system;  

import socket;  
import select;  
import time;     
import sys; 


class State(Enum):
    CONTINUE = 1
    EXIT = 2 

input_speech = str();   

VOICE_COMMANDS = VoiceCommands(); #.import_commands(); 
 
CONFIG, SOCK, CONN, ADDR = util.initialize_server();  
LISTENER = listener.CommandListner(CONN, VOICE_COMMANDS); 

LISTENER_STATUS = util.Detection(); 

#############################################
#               Thread Work                 #
#############################################

def thread_network_handler(): thread_socket_listener();  

THREAD_NETWORK = thread(target=thread_network_handler, args=[]);    

################################################

def initialize_threads():
    THREAD_NETWORK.start();  

def kill_threads():
    LISTENER_STATUS.stop_threads = True;  
    THREAD_NETWORK.join(); 

#################################################
#####               SPEECH                  #####
#################################################

def output_speech(text: str): 
    print("Assistant:", text); 
    CONN.sendall(bytes(util.get_token("CLIENT_SPEAK", util.Source.SERVER, util.Source.CLIENT) + "|" + text, "utf-8")); 

#################################################
#####               Network                 #####
#################################################

def network_sendall(message):
    CONN.sendall(bytes(message, 'utf-8')); 
    println("Network", "Sending packet{" + str(len(message)) + " byte(s)} with a message of", message); 

def thread_socket_listener(): 
    print("Now Listening from client");  
    while True:
        #THIS IS THE THREAD KILLER, IMPORTANT
        if LISTENER_STATUS.stop_threads == True: break; 

        print("Timeout, listening again"); 
        readySocks, _, _ = select.select([CONN], [], [], 5); 
        for sock in readySocks:   
            process_network_packet(sock); 
        
#####################################################################
#####                   RECEIVE NETWORK PACKET                  #####
#####################################################################

def process_network_packet(sock:socket.socket):
    println("NETWORK", "receiving packets...");  
    data = sock.recv(1024);         
    message = data.decode("utf-8");  

    print("received: " , message); 

    if util.get_token_raw("KEY_TOKEN") not in message:
        print_warning("Network", "Received an invalid packet. Ignoring."); 
        return; 

    header, source, destination, tags, body, args = util.parse_packet_message(message);   

    if destination != util.get_token_raw("SERVER_TOKEN"):
        print_warning("Network", "Received packet(s) intended for clients. Ignoring..."); 
        print(destination); 
        return; 

    if "*FUNC" in tags:
        return globals()[body.lower()](args); 
 
    #if body in util.get_raw_token("RETURN_REQUEST_SENTENCE_LOOP"):
    #    spoken_sentence = args[0]; 
    #    process_spoken_sentence_loop(spoken_sentence);  

    elif body in util.get_token_raw("RETURN_REQUEST_SENTENCE"):
        spoken_sentence = args[0]; 
        println("Network", "RETURN_REQUEST_SENTENCE found with the sentence of", spoken_sentence); 

        if util.get_token_raw("TIMEOUT") in spoken_sentence: 
            LISTENER_STATUS.set_ready_timeout(); 
        else: 
            response = LISTENER.get_response(spoken_sentence); 
            print(response.result); 
            LISTENER_STATUS.set_ready(response); 
    else:
        pass; 

###########################################################
#####                PRIMARY Methods                  #####
###########################################################

def process_result(response:listener.Response):  
    if response.result == Result.SUCCESS or response.result == Result.CONTINUE:  
        print("     User:", response.spoken_sentence); 
        print("  Command:", response.trigger_command); 
        output_speech(response.response_text); 
    elif response.result == Result.EXIT: 
        output_speech("Okay"); 
    elif response.result == Result.RELOAD: 
        VOICE_COMMANDS.reload(); 
        output_speech(response.response_text); 
    else: 
        output_speech("Sorry, I didn't pick up what you said."); 
    return State.CONTINUE;  

####################################################################
#                       NETWORK FUNCTIONS                          #
####################################################################

def network_process_spoken_sentence(args): 
    spoken_sentence:str = args[0]; 


    if util.get_token_raw("TIMEOUT") in args: 
        output_speech("Sorry, I didn't pick up what you said."); 
        return; 

    #this means that this is not a loop.
    is_loop = len(args) > 1; 
    print(args); 

    if not is_loop:
        response = LISTENER.on_receive_spoken_sentence(spoken_sentence); 
        process_result(response); 
        return State.CONTINUE;  

    trigger_word = args[1]; 
    response:listener.Response = LISTENER.on_receive_spoken_sentence_loop(spoken_sentence, [trigger_word], exit_commands=[]); 

    if response.result == Result.SUCCESS:  
        print("     User:", spoken_sentence); 
        output_speech('how may I help');   
        #response = LISTENER_REQUEST_SENTENCE_WAIT(timeout = 5); 
        LISTENER.request_response_from_clients(timeout=10);  

    elif response.result == Result.CONTINUE or response.result == Result.RELOAD:
        process_result(response);  
    elif response.result == Result.EXIT:
        output_speech("See you next time."); 
        return State.EXIT; 
    else:
        print_error("Processing Spoken Sentence", "How is this called????"); 
        pass; 
    
    #If not exit then it has to be continue; 
    return State.CONTINUE;   
    
def main(): 
    initialize_threads();  

    while(True): 
        stop_process = None; #listener_function(); 
        if(stop_process == State.EXIT): break;  

    CONN.sendall(bytes(util.get_token("STOP_SIGNAL", util.Source.SERVER, util.Source.CLIENT), "utf-8")); 
    SOCK.close();   
    
    THREAD_NETWORK.join();   

# end function 


try:
    if __name__ == '__main__': 
        main(); 
except Exception as e:
    print_error("SYSTEM", "The Server has crashed unexpectedly."); 
    print("ERROR:", e); 
    print("\nRestarting...");  
    #network_sendall(util.get_token("STOP_SIGNAL", util.Source.SERVER));  
    kill_threads(); 
    
    system(f"py {util.PARENT_DIR}/start.py") 
    sys.exit("STOPPING!"); 
