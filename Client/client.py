from xml.dom import NotFoundErr
import speech_recognition;  
import socket;
import select;
import time;
import pickle; 
from enum import Enum;
from Modules import client_resource_importer as resources; 
from Modules import text_to_speech;
from AudioPlayer import audio_player;

HOST = "localhost"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
ACK_TEXT = 'text_received'
 
def get_token(token_string:str): 
    return resources.get_token(token_string); 

def listen_sentence_input(recognizer:speech_recognition.Recognizer, microphone:speech_recognition.Microphone, timeout): 
    
    try:
        with microphone as source:
            recorded_audio = recognizer.listen(source, timeout = timeout);  
            spoken_sentence = recognizer.recognize_google(recorded_audio); 
            return spoken_sentence; 

    except (speech_recognition.UnknownValueError, speech_recognition.WaitTimeoutError):
        return "NULL"; 
 
def send_data(data):   
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT)); 
        s.sendall(bytes(data)); 
        return_data = s.recv(1024); 
 
    return return_data; 

def main(): 
    global recognizer, microphone, stop_process; 
    recognizer = speech_recognition.Recognizer(); 
    microphone = speech_recognition.Microphone();  
    resources.update_token(); 
    
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
            pass 

    loop(sock);   

def loop(sock:socket.socket): 
    socks = [sock]; 
    stop = False; 
    while stop == False:    
        print("Listening", end="\r");  
        #wait here
        readySocks, _, _ = select.select(socks, [], [], 1); 

        for sock in readySocks:
        #loop_listen
            message = receive_request(sock, recognizer,microphone); 
            #print('Finished Executing: ' + str(message));  

##################################################################
###################    PROCESS FUNCTIONS      ####################
##################################################################

def process_packet(packet_message):
    splits = packet_message.split("|"); 
    title = splits[1].strip().upper(); 

    function_string = ""; 

    if "*FUNC" in title:
        function_string = title[title.index(":") + 1:]; 

    if "*ARGS" not in title:
        return (title, list(), function_string);  

    args = splits[2].split('/'); 
    return (title, args, function_string); 

def query_arguments(key, args):
    for arg in args:
        arg = arg.strip(); 
        if key in arg:
            split = arg.split('='); 
            try:
                return split[1]; 
            except:
                raise Exception("Arguements pass down must be dictated with '=' sign to assign!\n" + "Got: " + arg);  
    raise NotFoundErr("You key doesn't exit!?"); 

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
    spoken_sentence = listen_sentence_input(recognizer, microphone, timeout); 

    print('sending audio...');  
    if(spoken_sentence == "NULL"):
        sock.sendall(bytes(get_token("TIMEOUT"), 'utf-8')); 
    else:
        sock.sendall(bytes(spoken_sentence, 'utf-8')); 
    
    return True; 

def network_speak(sock:socket.socket, args:list):            
    text_to_speech.create_sentence_wave(args[0]);  
    audio_player.play_generated_sentence();      

def network_exit(sock:socket.socket, args:list):
    sock.close(); 
    return True;  

####################################################################
#                           REQUEST HANDLERS                       #
####################################################################

import re;

def receive_request(sock: socket.socket, recognizer, microphone):
    # get the text via the scoket
    encodedMessage = sock.recv(1024); 

    if not encodedMessage:
        print('error: encodedMessage was received as None'); 
        return "None";  

    # decode the received text message
    message = encodedMessage.decode('utf-8'); 

    print("Received", message, "from the server"); 

    if get_token("KEY_TOKEN") not in message: 
        print("Received something that is not a request. Message:", message); 
        return "None"; 

    token_occurance = [occurance.start() for occurance in re.finditer(get_token("KEY_TOKEN"), message)]; 
    length = len(token_occurance)
    for i in range(length): 
        occur_index = token_occurance[i];  
        tokened_message = str();  

        if i + 1 == length:
            tokened_message = message[occur_index:]; 
        else:
            next_index = token_occurance[i + 1]; 
            tokened_message = message[occur_index:next_index]; 

        title, args, function_string = process_packet(tokened_message); 
    
        if function_string == "":
            continue;  #if it is a function
        if globals()[function_string.lower()](sock, args) == False:
            raise Exception("Something went definately wrong, check it.");  

# end function

if __name__ == '__main__': 
    main(); 