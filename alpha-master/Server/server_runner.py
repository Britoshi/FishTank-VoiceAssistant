import multiprocessing
from pickle import FALSE; 
 
from Core import utility as util;  
util.update_token();  

from Modules import text_to_speech; 
from AudioPlayer import audio_player; 
from Core import command_listener as listener; 
from enum import Enum; 
from Core.server_system import *; 
from Core.command import *; 
from Core.custom_thread import StoppableThread as thread;

import socket;  
import select;  
import time;     
import sys;

import speech_recognition as speech_recognition_module;   


class State(Enum):
    CONTINUE = 1
    EXIT = 2 

input_speech = str();  

RECOGNIZER = speech_recognition_module.Recognizer();   

VOICE_COMMANDS = VoiceCommands(); #.import_commands(); 
 
CONFIG, SOCK, CONN, ADDR = util.initialize_server();  
LISTENER = listener.CommandListner(CONN, VOICE_COMMANDS); 

LISTENER_STATUS = util.Detection(); 

#############################################
#               Thread Work                 #
#############################################

def thread_network_handler(): thread_socket_listener(); 
def thread_speech_handler(): thread_speech_processor();  

THREAD_NETWORK = thread(target=thread_network_handler, args=[]); 
THREAD_SPEECH = thread(target=thread_speech_handler, args=[]);    

################################################

def initialize_threads():
    THREAD_NETWORK.start(); 
    THREAD_SPEECH.start(); 

def kill_threads():
    LISTENER_STATUS.stop_threads = True; 
    THREAD_SPEECH.join(); 
    THREAD_NETWORK.join(); 

#################################################
#####               SPEECH                  #####
#################################################

def thread_speech_processor():
    global input_speech; 
    while(True): 
        #THIS IS THE THREAD KILLER, IMPORTANT
        if LISTENER_STATUS.stop_threads == True: break; 

        if(input_speech == ""): continue;  
        #if(stop_process == State.EXIT): break; 

        print("Assistant:", input_speech);                  
        text_to_speech.create_sentence_wave(input_speech);  
        audio_player.play_generated_sentence();             
        input_speech = "";                                  


def output_speech(text: str): 
    print("Assistant:", input_speech);       
    CONN.sendall(bytes(util.get_token("CLIENT_SPEAK", util.Source.SERVER) + "|" + text, "utf-8")); 

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
        

def process_network_packet(sock:socket.socket):
    println("NETWORK", "receiving packets...", end = " ");  
    data = sock.recv(1024);         
    message = data.decode("utf-8");  

    print("received: " , message); 

    if util.get_token("KEY_TOKEN") not in message:
        print_warning("Network", "Received an invalid packet. Ignoring."); 
        return; 

    header, source, tags, body, args = util.parse_packet_message(message);   

    if source != util.get_token("CLIENT_TOKEN"):
        print_warning("Network", "Received packet from server, receiving self packets. Just ignoring.")
        return; 

    if "*FUNC" in tags:
        print("Run function, not implemented");  
        return globals[body.lower()](args); 
 
    if body in util.get_raw_token("RETURN_REQUEST_SENTENCE"):
        spoken_sentence = args[0]; 
        println("Network", "RETURN_REQUEST_SENTENCE found with the sentence of", spoken_sentence); 

        if util.get_raw_token("TIMEOUT") in spoken_sentence: 
            LISTENER_STATUS.set_ready_timeout(); 
        else: 
            response = LISTENER.get_response(spoken_sentence); 
            print(response.result); 
            LISTENER_STATUS.set_ready(response); 
    else:
        pass; 

#######################################################
#####               Main Methods                  #####
#######################################################

def process_result():  
    if LISTENER_STATUS.result == Result.SUCCESS or LISTENER_STATUS.result == Result.CONTINUE:  
        print("     User:", LISTENER_STATUS.spoken_sentence); 
        print("  Command:", LISTENER_STATUS.trigger_command); 
        output_speech(LISTENER_STATUS.response_text); 
    elif LISTENER_STATUS.result == Result.EXIT: 
        output_speech("Okay"); 
    elif LISTENER_STATUS.result == Result.RELOAD: 
        VOICE_COMMANDS.reload(); 
        output_speech(LISTENER_STATUS.response_text); 
    else: 
        output_speech("Sorry, I didn't pick up what you said."); 
    return State.CONTINUE; 

def LISTENER_REQUEST_SENTENCE_WAIT(fishtank_seek = False, timeout = LISTENER.loop_timeout): 
    LISTENER.request_response_from_clients(timeout=timeout); 
    LISTENER_STATUS.wait();  
    #this has to come after wait; 
    if fishtank_seek: LISTENER_STATUS.fishtank_seek = True; 
    #add a timeout to this later 
    start_time = time.time(); 
    while LISTENER_STATUS.ready == False: 
        curr_time = time.time(); 
        difference = curr_time - start_time; 
        if difference > 60:
            raise Exception("Something went terribly wrong. There's a high probability that the problem is caused by the client.")

    return Result.SUCCESS; 

def fishtank_listener():  
    request = LISTENER_REQUEST_SENTENCE_WAIT(fishtank_seek=True);   
    #this will be added into the method itself later
    if request != Result.SUCCESS: raise Exception("Something went wrong inside the waiting sequence for sentence. Contact Brian."); 

    response = LISTENER.on_receive_spoken_sentence_loop(LISTENER_STATUS.spoken_sentence, ["fish tank"], exit_commands=[]); 
    if response.result == Result.SUCCESS:  
        print("     User:", LISTENER_STATUS.spoken_sentence); 
        output_speech('how may I help');  

        request = LISTENER_REQUEST_SENTENCE_WAIT(timeout = 5);  
        process_result();  
    elif response.result == Result.CONTINUE or response.result == Result.RELOAD:
        process_result();  
    elif response.result == Result.EXIT:
        output_speech("See you next time."); 
        return State.EXIT; 
    else:
        pass; 
    
    #If not exit then it has to be continue; 
    return State.CONTINUE; 

def listener_function():  
    #this might be hard to read, but if the loop is returned to stop, then stop.
    raise Exception("TEST"); 
    if(fishtank_listener() == State.EXIT): return State.EXIT; 

def main(): 
    initialize_threads();  

    while(True): 
        stop_process = listener_function(); 
        if(stop_process == State.EXIT): break;  

    CONN.sendall(bytes(util.get_token("STOP_SIGNAL", util.Source.SERVER), "utf-8")); 
    SOCK.close();   
    
    THREAD_NETWORK.join();  
    THREAD_SPEECH.join();  

# end function 

from os import system;  

try:
    if __name__ == '__main__': 
        main(); 
except Exception as e:
    print_error("SYSTEM", "The Server has crashed unexpectedly."); 
    print("ERROR:", e); 
    print("\nRestarting...");  
    network_sendall(util.get_token("")) 
    kill_threads(); 
    
    system(f"py {util.PARENT_DIR}/start.py") 
    sys.exit("STOPPING!"); 
