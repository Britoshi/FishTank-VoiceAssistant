import threading; 
import time;  
 
from Modules import resource_importer, text_to_speech; 
from AudioPlayer import audio_player; 
from Core import command_listener as listener; 
from enum import Enum; 

import socket;  
import select;  
import time;    
import pickle;  

import speech_recognition as speech_recognition_module;  
import pyaudio; 

class State(Enum):
    CONTINUE = 1
    EXIT = 2 

input_speech = str(); 

stop_process = State; 
waiting_for_speech = False; 

recognizer = speech_recognition_module.Recognizer();  

voice_commands = list(); 
 
HOST = "localhost"; #"192.168.1.141"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
ACK_TEXT = 'text_received'; 

#############################################
#               Thread Work                 #
#############################################

def assistant_speech_processor():
    global input_speech, stop_process; 
    while(True): 
        if(input_speech == ""):
            continue; 

        if(stop_process == State.EXIT):
            break; 

        print("Assistant:", input_speech);                  
        text_to_speech.create_sentence_wave(input_speech);  
        audio_player.play_generated_sentence();             
        input_speech = "";                                  

def waiting_for_speech_animation():
    global stop_process, waiting_for_speech; 
    animation = "|/-\\" 
    idx = 0 
    print("Testing Thread"); 
    while True:
        if(stop_process == State.EXIT):
            break; 
        
        output_text = "Speaking ";  
        if(waiting_for_speech == True):  
            output_text = "Listening ";   
        print(output_text + animation[idx % len(animation)], end = "\r");  
        
        idx += 1; 
        time.sleep(0.1);  

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
    sock.sendall(bytes(resource_importer.get_token("CLIENT_SPEAK") + "|" + text, "utf-8")); 

def fishtank_listener(conn:socket.socket):

    def process_result(response: listener.Response):  
        if response.result == listener.Result.SUCCESS or response.result == listener.Result.CONTINUE:  
            print("     User:", response.spoken_sentence);    
            print("  Command:", response.trigger_command); 
            output_speech(conn, response.response_text);    
        elif response.result == listener.Result.EXIT:
            output_speech(conn, "Okay"); 
        else:
            output_speech(conn, "Sorry, I didn't pick up what you said."); 

        return State.CONTINUE;  

    global voice_commands;  

    loop_response = listener.voice_recognition_detect_loop(conn, voice_commands, recognizer, ["fish tank", "fishtank"], 3, exit_commands=["stop", "exit"]); 
    if loop_response.result == listener.Result.SUCCESS:
        
        text = "how may I help?"; 
        print("     User:", loop_response.spoken_sentence); 
        output_speech(conn, text);  

        response = listener.voice_recognition_detect(conn, voice_commands); 
        process_result(response); 

    elif loop_response.result == listener.Result.CONTINUE:
        process_result(loop_response); 
    else:
        output_speech(conn, "See you next time."); 
        return State.EXIT; 
    
    #If not exit then it has to be continue; 
    return State.CONTINUE; 

def listener_function(conn:socket):  
    #this might be hard to read, but if the loop is returned to stop, then stop.
    if(fishtank_listener(conn) == State.EXIT):
        return State.EXIT; 

def initialize_socket(): 
    # instantiate a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('socket instantiated') 
    sock.bind((HOST, PORT))
    print('socket binded') 
    sock.listen()
    print('socket now listening') 
    conn, addr = sock.accept()#wait
    print('socket accepted, got connection object')

    return (sock, conn, addr); 

def main(): 
    global stop_process, voice_commands;  
    voice_commands = resource_importer.parse_commands(); 
    resource_importer.update_token(); 

    thread_main_listener = threading.Thread(target=assistant_speech_processor, args=[]); 
    thread_main_listener.start(); 

    #speech_wait = threading.Thread(target=waiting_for_speech_animation, args=[]); 
    #speech_wait.start();    
    #speech_wait.join(); 

    sock, conn, addr = initialize_socket(); 
    
    #socket_thread = threading.Thread(target=thread_socket_listener, args=[conn]); 
    #socket_thread.start();    

    while(True): 
        stop_process = listener_function(conn); 
        if(stop_process == State.EXIT):
            break; 

    thread_main_listener.join();  

    conn.sendall(bytes(resource_importer.get_token("STOP_SIGNAL"), "utf-8")); 
    #socket_thread.join(); 

# end function 

if __name__ == '__main__': 
    main(); 