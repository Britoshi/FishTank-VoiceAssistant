import threading; 
import time;  
 
from Core import utility as util; 
from Modules import text_to_speech; 
from AudioPlayer import audio_player; 
from Core import command_listener as listener; 
from enum import Enum; 
from Core.server_system import *; 
from Core.command import *;

import socket;  
import select;  
import time;     

import speech_recognition as speech_recognition_module;   

class State(Enum):
    CONTINUE = 1
    EXIT = 2 

input_speech = str(); 

stop_process = State; 
waiting_for_speech = False; 

recognizer = speech_recognition_module.Recognizer();  

voice_commands = list(); 

CONFIG = util.Configuration.load_config(); 

HOST = CONFIG.HOST_IP; #"192.168.1.141"  # Standard loopback interface address (localhost)
PORT = CONFIG.PORT  # Port to listen on (non-privileged ports are > 1023)

ACK_TEXT = 'text_received'; 

#############################################
#               Thread Work                 #
#############################################

def thread_speech_processor():
    global input_speech, stop_process; 
    while(True): 
        if(input_speech == ""): continue;  
        if(stop_process == State.EXIT): break; 

        print("Assistant:", input_speech);                  
        text_to_speech.create_sentence_wave(input_speech);  
        audio_player.play_generated_sentence();             
        input_speech = "";                                   

def thread_socket_listener(conn:socket.socket): 
    print("Now Listening from client"); 

    exit = False; 
    while exit == False:  
        while True: 
            data = conn.recv(1024); 

            if not data:
                break; 

            ackText = data.decode('utf-8'); 

            if ackText == "stop":
                exit = True; 

            if(ackText == ACK_TEXT): 
                print(ackText); 
                break; 
            else:
                conn.sendall(data);  

def output_speech(sock:socket.socket, text: str): 
    print("Assistant:", input_speech);       
    sock.sendall(bytes(util.get_token("CLIENT_SPEAK") + "|" + text, "utf-8")); 

def fishtank_listener(conn:socket.socket): 

    global voice_commands;  

    def process_result(response: listener.Response):  
        if response.result == Result.SUCCESS or response.result == Result.CONTINUE:  
            print("     User:", response.spoken_sentence);    
            print("  Command:", response.trigger_command); 
            output_speech(conn, response.response_text);    
        elif response.result == Result.EXIT:
            output_speech(conn, "Okay"); 
        elif response.result == Result.RELOAD: 
            global voice_commands;  
            voice_commands = VoiceCommand.import_commands(); 
            output_speech(conn, response.response_text); 
        else:
            output_speech(conn, "Sorry, I didn't pick up what you said."); 

        return State.CONTINUE;  

    loop_response = listener.voice_recognition_detect_loop(conn, voice_commands, recognizer, ["fish tank"], 10, exit_commands=[]); 
    if loop_response.result == Result.SUCCESS: 
        print("     User:", loop_response.spoken_sentence); 
        output_speech(conn, 'how may I help');  

        response = listener.voice_recognition_detect(conn, voice_commands); 
        process_result(response); 

    elif loop_response.result == Result.CONTINUE or loop_response.result == Result.RELOAD:
        process_result(loop_response); 
    else:
        output_speech(conn, "See you next time."); 
        return State.EXIT; 
    
    #If not exit then it has to be continue; 
    return State.CONTINUE; 

def listener_function(conn:socket):  
    #this might be hard to read, but if the loop is returned to stop, then stop.
    if(fishtank_listener(conn) == State.EXIT): return State.EXIT; 

def initialize_socket(): 
    # instantiate a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    println("NETWORK",'Socket Instantiated') 
    sock.bind((HOST, PORT)) 
    sock.listen()
    println("NETWORK",'Socket Now Listening') 
    conn, addr = sock.accept()#wait
    println("NETWORK",'Socket Accepted, Got Connection Object')

    return (sock, conn, addr); 

def main(): 
    global stop_process, voice_commands;  
    voice_commands = VoiceCommand.import_commands(); 
    util.update_token(); 

    thread_network_listen = threading.Thread(target=thread_socket_listener, args=[]); 
    thread_speech_listen = threading.Thread(target=thread_speech_processor, args=[]); 
    thread_network_listen.start(); 
    thread_speech_listen.start(); 
 
    sock, conn, addr = initialize_socket(); 
     
    while(True): 
        stop_process = listener_function(conn); 
        if(stop_process == State.EXIT): break; 

    thread_network_listen.join();  
    thread_speech_listen.join();  

    conn.sendall(bytes(util.get_token("STOP_SIGNAL"), "utf-8")); 
    sock.close();  

# end function 

if __name__ == '__main__': 
    main(); 