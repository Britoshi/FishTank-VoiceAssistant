from xml.dom import NotFoundErr
import speech_recognition;  
import socket;
import select;
import time;
import pickle; 
from enum import IntEnum;
from Modules import utility as util; 
from Modules import text_to_speech;
from AudioPlayer import audio_player;
from os import system;   
import sys;

CONFIG = util.Configuration.load_config(); 

HOST = CONFIG.HOST_IP; 
PORT = CONFIG.PORT; 

ACK_TEXT = 'text_received'
 
RECOGNIZER = speech_recognition.Recognizer(); 
MICROPHONE = speech_recognition.Microphone();  

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
            recorded_audio = RECOGNIZER.listen(source, timeout = timeout);  
            spoken_sentence = RECOGNIZER.recognize_google(recorded_audio); 
            return spoken_sentence; 

    except (speech_recognition.UnknownValueError, speech_recognition.WaitTimeoutError):
        return None; 
 
def send_data(data):   
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT)); 
        s.sendall(bytes(data)); 
        return_data = s.recv(1024); 
 
    return return_data; 

def main():  
    util.update_token(); 
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); 
    print('socket instantiated'); 

    # connect the socket
    connectionSuccessful = False
    while not connectionSuccessful:
        try:
            sock.connect((HOST, PORT))    # Note: if execution gets here before the server starts up, this line will cause an error, hence the try-except
            print('socket connected'); 
            connectionSuccessful = True
        except:
            pass; 

    machine_state = State.CONTINUE;  
    while True: #machine_state != State.EXIT:   
        readySocks, _, _ = select.select([sock], [], [], 1); 
        for sock in readySocks: 
            states = receive_request(sock);   
            
            if State.FAIL in states:
                raise Exception("Something went definately wrong, check it.");   
            machine_state = states[-1];  

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

def receive_request(sock: socket.socket):
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
    print("SYSTEM", "The Server has crashed unexpectedly."); 
    print("ERROR:", e); 
    print("\nRestarting...");  
    #network_sendall(util.get_token("STOP_SIGNAL", util.Source.SERVER));  
    
    system(f"py {util.PARENT_DIR}/start.py") 
    sys.exit("STOPPING!"); 
