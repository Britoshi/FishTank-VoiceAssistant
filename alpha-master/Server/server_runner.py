from calendar import isleap
from httplib2 import Response
from Core import utility as util;  
#util.update_token();  
 
from Modules import discord_integration as discord;
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
import re; 

class State(Enum):
    CONTINUE = 1
    EXIT = 2 

input_speech = str();   

VOICE_COMMANDS = VoiceCommands(); #.import_commands(); 
 
CONFIG, SOCK, CONN, ADDR = util.initialize_server();  
LISTENER = listener.CommandListner(CONN, VOICE_COMMANDS); 

LISTENER_STATUS = util.Detection(); 

DISCORD = discord.DiscordServerAPI(); 

#############################################
#               Thread Work                 #
#############################################

def thread_network_handler(): thread_socket_listener();  

THREAD_NETWORK = thread(target=thread_network_handler, args=[]);    

################################################

def initialize_threads():
    THREAD_NETWORK.start();  

def initialize_discord():
    if len(CONFIG.DISCORD_TOKEN.strip()) < 1 or CONFIG.DISCORD_CHANNEL_ID == -1:
        print_warning("Discord", "Improper config for discord. Please check again. Disabling discord integration."); 
        return; 

    message = f"{util.get_token('DISCORD_INIT', util.Source.SERVER, util.Source.CLIENT)}|TOKEN={CONFIG.DISCORD_TOKEN}|CHANNEL_ID={CONFIG.DISCORD_CHANNEL_ID}|{DISCORD.users_to_list()}"; 
    network_sendall(message); 

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
 
        readySocks, _, _ = select.select([CONN], [], [], 5); 
        for sock in readySocks:   
            process_network_packet(sock); 
        
#####################################################################
#####                   RECEIVE NETWORK PACKET                  #####
#####################################################################

def __process_packet(socket, line): 
    header, source, destination, tags, body, args = util.parse_packet_message(line);  

    if destination != util.get_token_raw("SERVER_TOKEN"):
        print("Received packet(s) intended for client, ignoring..."); 
        return;  
    if "*FUNC" not in tags:
        return;  #if it isn't a function   
    return globals()[body.lower()](args);  

def process_network_packet(sock:socket.socket):
    println("NETWORK", "receiving packets...");  
    data = sock.recv(1024);         
    message = data.decode("utf-8");  

    print("received: " , message); 

    if util.get_token_raw("KEY_TOKEN") not in message:
        print_warning("Network", "Received an invalid packet. Ignoring."); 
        return;     
    
    status_list = [];  
    token_occurrence = [occurrence.start() for occurrence in re.finditer(util.get_token_raw("KEY_TOKEN"), message)];

    print("OCCURRENCE", token_occurrence); 
    length = len(token_occurrence)

    '''
    *Note

    This is only going to happen since I receive a packet size of 1024 bytes. If the two packets those were sent are smaller than
    or totals up to 1024 bytes, then they'll be packed into one packet. So I have to split the two using the header packet and 
    process them separately.
    '''
    for i in range(length): 
        occur_index = token_occurrence[i];  
        current_packet_message = str();  

        if i + 1 == length:
            current_packet_message = message[occur_index:]; 
        else:
            next_index = token_occurrence[i + 1]; 
            current_packet_message = message[occur_index:next_index];  

        status_check = __process_packet(sock, current_packet_message); 
        status_list.append(status_check);  

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

def network_discord_approve_user(args):
    user_id = args[0]; 
    DISCORD.add_user(user_id); 
    return State.CONTINUE; 

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

#####################################################################
#####                        MAIN RUNNER                        #####
#####################################################################

def main(): 
    initialize_threads();   
    #This is to make sure the client knows of all users; 
    initialize_discord(); 


    while(True): 
        stop_process = None; 
        if(stop_process == State.EXIT): break;  

    CONN.sendall(bytes(util.get_token("STOP_SIGNAL", util.Source.SERVER, util.Source.CLIENT), "utf-8")); 
    SOCK.close();   
    
    THREAD_NETWORK.join();    


try:
    if __name__ == '__main__': 
        main(); 
except Exception as e:
    print_error("SYSTEM", "The Server has crashed unexpectedly."); 
    print("ERROR:", e); 
    print("\nRestarting...");  
    #network_sendall(util.get_token("STOP_SIGNAL", util.Source.SERVER));  
    kill_threads(); 
    
    util.start_python_script(f"{util.PARENT_DIR}/start.py") 
    sys.exit("STOPPING!"); 
