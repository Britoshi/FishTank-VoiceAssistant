from xml.dom import NotFoundErr
import speech_recognition;  
import socket;
import select;
import time;
import pickle;
import threading;  
from enum import IntEnum;
from Modules import utility as util; 
util.update_token(); 

from Modules import text_to_speech;
from AudioPlayer import audio_player;
from os import system;   
import sys;

CONFIG = util.Configuration.load_config(); 

HOST = CONFIG.HOST_IP; 
PORT = CONFIG.PORT;  
 
RECOGNIZER = speech_recognition.Recognizer(); 
MICROPHONE = speech_recognition.Microphone();  

RECOGNIZER.dynamic_energy_threshold = False; 
RECOGNIZER.energy_threshold = 400;  

CLIENT_VARIABLE = util.ClientGlobalVariables();  

SOCK = util.initialize_network(HOST, PORT); 

#################################################################
#####                      CLIENT THREAD                    #####
#################################################################

def thread_network_handler(): thread_socket_listener(); 
def thread_noise_handler(): thread_noise_adjuster ();  

THREAD_NETWORK = threading.Thread(target=thread_network_handler, args=[]);    
THREAD_NOISE = threading.Thread(target=thread_noise_handler, args=[]); 

LOCK = threading.Lock(); 

#################################################################

def initialize_threads():
    THREAD_NETWORK.start();  
    THREAD_NOISE.start(); 


def kill_threads():
    CLIENT_VARIABLE.stop_threads = True;  
    THREAD_NETWORK.join(); 
    THREAD_NOISE.join(); 

#################################################################
#####                      THREAD WORKS                     #####
#################################################################

def thread_socket_listener():
    machine_state = State.CONTINUE;  
    while True:
        if CLIENT_VARIABLE.stop_threads: break; 

        readySocks, _, _ = select.select([SOCK], [], [], 1); 
        for sock in readySocks: 
            states = receive_request(sock);   
            
            if State.FAIL in states:
                raise Exception("Something went definitely wrong, check it.");   

            machine_state = states[-1];    

def thread_noise_adjuster():
    refresh_thresh_hold = 15; 
    seconds_interval = 1; 

    seconds_passed = 0; 
    while CLIENT_VARIABLE.stop_threads == False: 
        if seconds_passed >= refresh_thresh_hold: 
            RECOGNIZER.adjust_for_ambient_noise(MICROPHONE, duration=5); 
        
        time.sleep(seconds_interval); 
        seconds_passed += seconds_interval; 

 


#################################################################
#####                       OTHER FUNC                      #####
#################################################################



def background_task_callback(recognizer, audio):  
    if not CLIENT_VARIABLE.loop_available: return;  

    spoken_sentence = str();  
    try:
        spoken_sentence = recognizer.recognize_google(audio);  
        print("PICKED UP:", spoken_sentence); 
    except speech_recognition.UnknownValueError:
        return; #print("Google Speech Recognition could not understand audio")
    except speech_recognition.RequestError as e:
        return; #print("Could not request results from Google Speech Recognition service; {0}".format(e))

    #Check if fishtank is in the sentence
    trigger_word = "fish tank"; 
    if trigger_word in spoken_sentence.lower():
        #First Check if the server recognizes any of the words. 
        CLIENT_VARIABLE.loop_available = False;  

        message = get_token("RETURN_REQUEST_SENTENCE_LOOP", util.Source.CLIENT) + "|"; 
        message += spoken_sentence + "|" + trigger_word;  

        SOCK.sendall(bytes(message, 'utf-8')); 
        
        #If it returns false
        #spoken_sentence = listen_sentence_input(timeout); 



    


def initialize_background_process():
    listener = RECOGNIZER.listen_in_background(MICROPHONE, background_task_callback); 


class State(IntEnum): 
    SUCCESS = 0     
    FAIL = 1     
    CONTINUE = 2
    EXIT = 3 

def get_token(token_string:str, source = None): 
    return util.get_token(token_string, source=source); 

def listen_sentence_input(timeout): 
    try:
        with MICROPHONE as source:
            RECOGNIZER.adjust_for_ambient_noise(MICROPHONE);    
            recorded_audio = RECOGNIZER.listen(source, timeout = timeout);  
            spoken_sentence = RECOGNIZER.recognize_google(recorded_audio); 
            return spoken_sentence; 

    except (speech_recognition.UnknownValueError, speech_recognition.WaitTimeoutError):
        return None;  

##################################################################
###################      MAIN FUNCTION        ####################
################################################################## 

def main():    
    initialize_threads(); 
    initialize_background_process(); 

    while CLIENT_VARIABLE.stop_threads == False:
        pass; 


    

##################################################################
###################    PROCESS FUNCTIONS      ####################
################################################################## 

def query_arguments(key, args):
    for arg in args:
        arg = arg.strip(); 
        if key in arg:
            split = arg.split('='); 
            try:
                return split[1]; 
            except:
                raise Exception("Arguments pass down must be dictated with '=' sign to assign!\n" + "Got: " + arg);  
    raise NotFoundErr("Your key doesn't exit!?"); 

#################################################################
#               NETWORK METHODS SEND BACK METHODS               #
#################################################################

def network_request_sentence(sock:socket.socket, args:list): 

    queried_value = query_arguments("TIMEOUT", args);   
    print(args); 
    timeout = float(queried_value); 

    # now time to send the acknowledgement 
    # encode the acknowledgement text 
    # send the encoded acknowledgement text 
    spoken_sentence = listen_sentence_input(timeout); 

    print('sending audio...');  
    if(spoken_sentence == None): 
        message = get_token("RETURN_REQUEST_SENTENCE", util.Source.CLIENT) + "|"; 
        message += get_token("TIMEOUT");  
        sock.sendall(bytes(message, 'utf-8')); 
    else: 
        message = get_token("RETURN_REQUEST_SENTENCE", util.Source.CLIENT) + "|"; 
        message += spoken_sentence;  
        sock.sendall(bytes(message, 'utf-8')); 
    
    return State.SUCCESS; 

def network_speak(sock:socket.socket, args:list):    
    
    #TEMP
    CLIENT_VARIABLE.loop_available = True;

    text_to_speech.create_sentence_wave(args[0]);  
    audio_player.play_generated_sentence();    
    return State.EXIT; 

def network_exit(sock:socket.socket, args:list):
    sock.close(); 
    return State.SUCCESS;  

####################################################################
#                           REQUEST HANDLERS                       #
####################################################################

import re;

def receive_request(sock):
    # get the text via the scoket
    encodedMessage = sock.recv(1024); 

    if not encodedMessage:
        print('error: encodedMessage was received as None'); 
        return "None";  

    # decode the received text message
    message = encodedMessage.decode('utf-8'); 

    print("Received", message, "from the server"); 

    if util.get_raw_token("KEY_TOKEN") not in message:  
        print("Received an invalid token. Message:", message); 
        return "None"; 
    
    return_list = []; 

    token_occurrence = [occurrence.start() for occurrence in re.finditer(util.get_raw_token("KEY_TOKEN"), message)]; 
    print("OCCURRENCE", token_occurrence); 
    length = len(token_occurrence)
    for i in range(length): 
        occur_index = token_occurrence[i];  
        tokened_message = str();  

        if i + 1 == length:
            tokened_message = message[occur_index:]; 
        else:
            next_index = token_occurrence[i + 1]; 
            tokened_message = message[occur_index:next_index]; 

        header, source, tags, body, args = util.parse_packet_message(tokened_message); 
    
        if "*FUNC" not in tags:
            continue;  #if it is a function 
        return_list.append(globals()[body.lower()](sock, args));  
    return return_list; 

# end function 


try: 
    if __name__ == '__main__': 
        main(); 
        
except Exception as e:
    print("SYSTEM", "The Client has crashed unexpectedly."); 
    print("ERROR:", e); 
    print("\nRestarting...");  
    #network_sendall(util.get_token("STOP_SIGNAL", util.Source.SERVER));  
    kill_threads(); 
    system(f"py {util.PARENT_DIR}/start.py") 
    sys.exit("STOPPING!"); 
