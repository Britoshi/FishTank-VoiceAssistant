from asyncio import wait_for
from xml.dom import NotFoundErr; 
import speech_recognition;  
import socket;
import select;
import time; 
import threading;  
from enum import IntEnum;
from Core import utility as util; 
#util.update_token(); 
from DiscordAPI import fish_tank_discord_api as discord; 
from Modules import text_to_speech;
from AudioPlayer import audio_player; 
from Core.client_system import *; 
from Core.InputCommand import InputCommand; 
import sys; 
import re;

CONFIG = util.Configuration.load_config(); 

HOST = CONFIG.HOST_IP; 
PORT = CONFIG.PORT;  
 
RECOGNIZER = speech_recognition.Recognizer(); 
RECOGNIZER_BACKGROUND = speech_recognition.Recognizer(); 
MICROPHONE = speech_recognition.Microphone();  
MICROPHONE_BACKGROUND = speech_recognition.Microphone();  

#RECOGNIZER.dynamic_energy_threshold = False; 
#RECOGNIZER.energy_threshold = 400;  

CLIENT_VARIABLE = util.ClientGlobalVariables();  

SOCK = util.initialize_network(HOST, PORT); 

DISCORD = discord.DiscordBot(); 
INPUT_COMMAND = InputCommand.import_commands(); 

#################################################################
#####                      CLIENT THREAD                    #####
#################################################################

def start_thread(func):
    try:
        func(); 
    except Exception as e:
        
        exception_type, exception_object, exception_traceback = sys.exc_info(); 
        filename = exception_traceback.tb_frame.f_code.co_filename; 
        line_number = exception_traceback.tb_lineno; 

        print_fatal_error("THREAD", e, f"\nfilename: {filename}.\nline number: {line_number}\n\n");  
        CLIENT_VARIABLE.exception = e; 
        CLIENT_VARIABLE.stop_threads = True;   
        DISCORD.stop(); 

def thread_network_handler(): thread_socket_listener();  
def thread_input(): thread_input_handler();  

THREAD_NETWORK = threading.Thread(target=start_thread, args=[thread_network_handler]);    
THREAD_INPUT = threading.Thread(target=start_thread, args=[thread_input]); 
#THREAD_NOISE = threading.Thread(target=thread_noise_handler, args=[]); 

LOCK = threading.Lock(); 

#####                           ENUM                        #####

class State(IntEnum): 
    SUCCESS = 0     
    FAIL = 1     
    CONTINUE = 2
    EXIT = 3  

#################################################################

def initialize_threads():
    THREAD_NETWORK.start();  
    THREAD_INPUT.start(); 
    #THREAD_NOISE.start(); 


def kill_threads():
    CLIENT_VARIABLE.stop_threads = True;  
    CLIENT_VARIABLE.stop_background_listener(wait_for_stop=False); 
    THREAD_NETWORK.join(); 
    THREAD_INPUT.join();  
    #THREAD_NOISE.join(); 

#################################################################
#####                      THREAD WORKS                     #####
#################################################################

def thread_socket_listener():
    machine_state = State.CONTINUE;  
    while CLIENT_VARIABLE.stop_threads == False or machine_state == State.EXIT: 

        readySocks, _, _ = select.select([SOCK], [], [], 1); 
        for sock in readySocks: 
            states = receive_packet(sock);   
            
            if State.FAIL in states:
                raise Exception("Something went definitely wrong, check it.");    
            machine_state = states[-1];    

def thread_noise_adjuster():
    #this is WIP, not functional
    return; 
    refresh_thresh_hold = 15; 
    seconds_interval = 1; 

    seconds_passed = 0; 
    while CLIENT_VARIABLE.stop_threads == False: 
        if seconds_passed >= refresh_thresh_hold: 
            RECOGNIZER.adjust_for_ambient_noise(MICROPHONE, duration=5); 
        
        time.sleep(seconds_interval); 
        seconds_passed += seconds_interval; 

#####################################################################
######                      INPUT COMMAND                       #####
#####################################################################

    

def parse_user_input(user_input):
    return user_input[user_input.index(" ") + 1:];  

def run_command(user_input = None): 
    try: 
        if user_input == None: 
            user_input = input();   
        content = parse_user_input(user_input);   
    except EOFError:
        print_warning("INPUT", "Escaping(Ctrl+Z/C) is not allowed. Please Type \"/stop\"."); 
    except ValueError:
        content = "";  

    INPUT_COMMAND.run(user_input, SOCK, content); 

def thread_input_handler(): 
    INPUT_COMMAND.set_function("say, speak", __network_send_return_sentence);  
    INPUT_COMMAND.set_function("silent, whisper, ask", __network_send_return_sentence_silent); 
    INPUT_COMMAND.set_function("help", INPUT_COMMAND.list_commands); 
    INPUT_COMMAND.set_function("stop, quit, exit", INPUT_COMMAND.stop);  

    while CLIENT_VARIABLE.stop_threads == False:
        run_command(); 

#################################################################
#####                       OTHER FUNC                      #####
#################################################################



def background_task_callback(recognizer:speech_recognition.Recognizer, audio):  
    if not CLIENT_VARIABLE.loop_available: return;  

    spoken_sentence = str();  
    try:
        spoken_sentence:str = recognizer.recognize_google(audio);  
        print("PICKED UP:", spoken_sentence); 
    except (speech_recognition.UnknownValueError, speech_recognition.RequestError):
        return; 

    #Check if fishtank is in the sentence
    trigger_word = "fish tank"; 
    if trigger_word in spoken_sentence.lower():
        #First Check if the server recognizes any of the words. 
        CLIENT_VARIABLE.loop_available = False;  
 
        message = spoken_sentence + "|" + trigger_word;    
        __network_send_return_sentence(SOCK, message); 

def initialize_background_process():
    CLIENT_VARIABLE.stop_background_listener = RECOGNIZER_BACKGROUND.listen_in_background(MICROPHONE_BACKGROUND, background_task_callback);  

def initialize_discord(): 
    DISCORD.info.network_function = __discord_send_sentence; 
    DISCORD.info.add_function = __discord_approve_user;  

    start_time = time.time(); 
    while DISCORD.info.token == None and CLIENT_VARIABLE.stop_threads == False:
        time.sleep(0.1); 
        curr_time = time.time(); 
        if curr_time - start_time > 60:
            print("Failed to start Discord.");  
            while CLIENT_VARIABLE.stop_threads == False:
                time.sleep(0.1);  
    
    client_success = False; 
    while client_success == False and CLIENT_VARIABLE.stop_threads == False:
        try: 
            DISCORD.run(DISCORD.info.token);    
            client_success = True; 
        except Exception as e:
            print_warning("DISCORD", "Most likely rate limited by Discord. Please wait until it retries...")
            time.sleep(10); 


def listen_sentence_input(timeout):  
    """
    Listens to the microphone with the given timeout in seconds.

    This function uses the speech_recognition module to listen and then recognize the words
    and return the sentence. If it fails to pick up any words or times out, then it'll return None.

    Parameters
    ----------
    timeout : float
        How long the recognizer will listen to until it times out.

    Returns
    -------
    str
        The spoken sentence of the speaker. This will return None if timeout occurs or recognizer fails to find a value.
    """
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
    initialize_discord(); 

    if CLIENT_VARIABLE.stop_threads:
        util.raise_error(CLIENT_VARIABLE.exception, "One of the threads have run into an error!"); 
    else:
        util.raise_error(Exception("Critical Discord Failure"), "This should never happen!!!"); 
    
        
##################################################################
###################    PROCESS FUNCTIONS      ####################
################################################################## 


def query_keyword_in_arguments(keyword:str, arguments:list):
    """
    Queries for the keyword in a given list.

    This function simply goes through the list of arguments sent in a network packet
    and return the value (separated by "=") of the argument if the keyword is inside.

    Parameters
    ----------
    keyword : str
        The keyword to query with.
    arguments : list
        The list of arguments passed from the network packet.

    Returns
    -------
    str
        The matched value tokened along side with the keyword.

    See Also
    --------
    network_request_sentence : An example function that uses this query function.

    Examples
    --------
    >>> query_keyword_in_arguments("FIRSTNAME", ["FIRSTNAME=Brian", "LASTNAME=Kim",...])
    "Brian"
    >>> query_keyword_in_arguments("PRICE", ["LOCATION=Irvine","PRICE=$120",...])
    "$120" 
    """
    for argument in arguments:
        argument = argument.strip(); 
        if keyword in argument:
            split = argument.split('='); 
            try:
                return split[1]; 
            except:
                raise Exception("Arguments pass down must be dictated with '=' sign to assign!\n" + "Got: " + argument);  
    raise NotFoundErr("Your key doesn't exit!?"); 

#################################################################
#               NETWORK METHODS SEND BACK METHODS               #
#################################################################

def network_sendall(message):
    SOCK.sendall(bytes(message, 'utf-8')); 
    println("Network", "Sending packet{" + str(len(message)) + " byte(s)} with a message of", message); 

#####                   PRIVATE                     #####

def __network_send_return_sentence(sock:socket.socket, spoken_sentence:str):
    message = util.get_token("RETURN_REQUEST_SENTENCE", util.Source.CLIENT, util.Source.SERVER) + "|"; 

    if(spoken_sentence == None): message += util.get_token_raw("TIMEOUT");  
    else: message += spoken_sentence;  

    sock.sendall(bytes(message, 'utf-8'));  

def __network_send_return_sentence_silent(sock:socket.socket, sentence:str):
    message = util.get_token("RETURN_REQUEST_SENTENCE", util.Source.CLIENT, util.Source.SERVER) + "|";  
    if(sentence == None): message += util.get_token_raw("TIMEOUT");  
    else: message += "fish tank " + sentence + "|SILENT"; 
    sock.sendall(bytes(message, 'utf-8')); 

def __discord_send_sentence(sentence):
    run_command(sentence);  

def __discord_approve_user(user_id):
    message = util.get_token("DISCORD_ADD", util.Source.CLIENT, util.Source.SERVER) + "|"; 
    message += user_id; 
    SOCK.sendall(bytes(message, 'utf-8')); 

#####                   PUBLIC                      #####

def network_request_sentence(sock:socket.socket, args:list):  
    queried_value = query_keyword_in_arguments("TIMEOUT", args); 
    timeout = float(queried_value);  

    spoken_sentence = listen_sentence_input(timeout); 

    __network_send_return_sentence(sock, spoken_sentence);  
    return State.SUCCESS; 

def network_speak(sock:socket.socket, args:list): 
    CLIENT_VARIABLE.loop_available = True; 

    sentence = args[0]; 
    DISCORD.write_message(sentence); 
    #If is silent, then don't speak it.
    if "SILENT" in args: return State.EXIT; 
    text_to_speech.create_sentence_wave(sentence);  
    audio_player.play_generated_sentence();    
    return State.EXIT; 

def network_discord_initialize(sock:socket.socket, args:list):
    discord_token = query_keyword_in_arguments("TOKEN", args); 
    channel_id = query_keyword_in_arguments("CHANNEL_ID", args); 
    users = args[2:]; 
    for user in users:
        DISCORD.info.add_user(user); 
    DISCORD.info.channel_id = int(channel_id); 
    DISCORD.info.token = discord_token; 


def network_exit(sock:socket.socket, args:list):
    sock.close(); 
    return State.SUCCESS;  

#######################################################################
#                           REQUEST HANDLERS                          #
#######################################################################

def __process_packet(socket, line): 
    header, source, destination, tags, body, args = util.parse_packet_message(line);  
    if destination != util.get_token_raw("CLIENT_TOKEN"):
        print("Received packet(s) intended for server, ignoring..."); 
        return;  
    if "*FUNC" not in tags:
        return;  #if it isn't a function  
    return globals()[body.lower()](socket, args); 

def receive_packet(sock):
    # get the text via the socket
    encodedMessage = sock.recv(1024 * 4); 

    if not encodedMessage:
        print('error: encodedMessage was received as None'); 
        return "None";  

    # decode the received text message
    message = encodedMessage.decode('utf-8'); 

    print("Received", message, "from the server"); 

    if util.get_token_raw("KEY_TOKEN") not in message:  
        print("Received an invalid token. Message:", message); 
        return "None"; 
    
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
    return status_list; 
 
try: 
    if __name__ == '__main__': 
        main(); 
        
except Exception as e:
    print("SYSTEM", "The Client has crashed unexpectedly."); 
    print("ERROR:", e); 
    print("\nRestarting...");  
    network_sendall(util.get_token("STOP_SIGNAL", util.Source.CLIENT, util.Source.SERVER));  
    kill_threads();  
    sys.exit("STOPPING!"); 
