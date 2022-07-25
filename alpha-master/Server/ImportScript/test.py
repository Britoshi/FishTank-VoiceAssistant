from command import *; 
import math

def power_two_numbers(spoken_sentence:str, command: VoiceCommand, args: list):
    first_number = int(args[0]); 
    second_number = int(args[1]); 

    result = math.pow(first_number, second_number); 
    return_sentence = f"The power of {first_number} to the {second_number} is {result}"; 
    return (Result.SUCCESS, return_sentence);  


vc = VoiceCommand(1, "fuck", "what is", power_two_numbers, VoiceCommand.Type.FREE, ["is", "^"]); 

spoken_sentence = "what is 3 ^ 5"

q_list = vc.query_for_words(spoken_sentence); 

print(q_list); 