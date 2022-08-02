

# 🗄️ FISHTANK VOICE ASSISTANT: SERVER 🗄️

This is the server section of the voice assistant. This is of course going to be running in the server of the lab.
 

# Voice Commands
One of the core components of the voice assistant is the voice command, ```VoiceCommand``` found in [command.py](./Core/command.py).

The Voice Command has 7 key components: 
1. [Priority](https://github.com/Britoshi/FishTank-VoiceAssistant/tree/main/alpha-master/Server#priority)
2. [Type](https://github.com/Britoshi/FishTank-VoiceAssistant/tree/main/alpha-master/Server#type)
3. [Trigger Words](https://github.com/Britoshi/FishTank-VoiceAssistant/tree/main/alpha-master/Server#trigger-words)
4. [Command Type](https://github.com/Britoshi/FishTank-VoiceAssistant/tree/main/alpha-master/Server#command-type)
5. [Import Script](https://github.com/Britoshi/FishTank-VoiceAssistant/tree/main/alpha-master/Server#import-script-name)
6. [Function](https://github.com/Britoshi/FishTank-VoiceAssistant/tree/main/alpha-master/Server#function)
7. [Query List](https://github.com/Britoshi/FishTank-VoiceAssistant/tree/main/alpha-master/Server#query-list)

If you do not know how the voice assistant work, please go back to [main page](../../README.md) and read the documentation there.
Once the client returns the spoken_sentence back to the server, the server will check whether the trigger word is a part of the spoken sentence and do more *additional checks* to make sure the server is going to run the correct command.

### Priority
```VoiceCommand.priority``` is an integer value. Most common commands will have a priority of 1. 
The priority value will be taken into account when putting the **load order** of the voice commands.

### Type
**Type** or known in the script as ```VoiceCommand.name``` is a simple categorization of what the Voice Command is used for.  
If the Voice Command revolves around weather functions, then the name most likely will be "Weather"

### Trigger Words
```VoiceCommand.trigger_word``` is the word or a sentence the Voice Command will use to determine if the voice command should pass the check.

### Command Type
```VoiceCommand.command_type``` is an enum value inside of the ```VoiceCommand``` Object: ```Type(IntEnum)```.  
It has two types corresponding to the integer value  
```
Type.STRICT = 1;
Type.FREE = 0; 
```
**Free Command** will be using the method of ```if``` **```self.trigger_word```** ```in``` **```spoken_sentence```**.
If any instance of the trigger word can be found in a given sentence, then the voice request will pass the check.

**Strict Command** requires the ```self.trigger_word``` to be the sole word in the ```spoken_sentence```.  
For example, if a strict command has a trigger word of "nevermind" and the spoken sentence is "FishTank... nevermind", then the strict command check will pass and run the strict command after going through a few *additional checks*. 

### Import Script
This is where things get more precise and important. ```VoiceCommand.script``` is where the script will be calling the ```VoiceCommand.function()``` from. This will match the script inside the [Import Script folder](./ImportScript/).

### Function
```VoiceCommand.function``` is the function that is run once all the checks from the spoken sentence and other additional checks are passed. This function has a strict structure that must be followed. They can be named anything, but must have 3 parameters: **```function(spoken_sentence:str, command: VoiceCommand, args: list)```** and it must return a **Result value** along with a string, **a sentence that the voice assistant will speak back to the user:** E.G. ```return (Result.SUCCESS, "Okay, pausing the song.")``` or ```return (1, "Okay, pausing the song.")```

#### Result Value
Result is an integer enum that can be found in the same file as **command.py**. 
```
class Result(IntEnum): 
    SUCCESS = 1     
    FAIL = 2        
    CONTINUE = 3    
    EXIT = 4        
    TIMEOUT = 5     
```

**IMPORTANT**: Know that VoiceCommand Function should ***NEVER*** return anything other than SUCCESS:1 or FAIL:2. If others are sent, the assistant will break!!!

If you did some additional checks inside your function and you deemed that it won't work, then you should return ```Result.FAIL```. By doing so, the server will just look for another command that it can use going down the order of available commands.

### Query List

```VoiceCommand.query_list``` is a list of list(s) that contains strings, example: ```[ [ "menu" ], [ "for", "at" ] ]```.
These become relevant when the ```VoiceCommand.function``` is called for the query list to dictate what gets passed down to the arguments in the  
```function(spoken_sentence:str, command: VoiceCommand,``` **```args: list)```*First, the server will check if the voice command has a query list. If the query list is an empty list, then it'll skip the check and pass down the empty list as the argument of the function.
If the query list is not empty like the example given above, then it'll **query** for words using the strings in the list.

Inside the query list, the first list is the ```[ "menu" ]```, since there's only one item in the list they'll do a single check on the **spoken_sentence**.
If the **spoken_sentence** that was sent from the client has a keyword in the list, in this case, the **menu**, then it'll take the words after the string **menu** until the end of the spoken_sentence or until the next keyword, in this case, those would be either **"for"** or **"at"**. After it takes the first batch, it will repeat for the next keyword which is the same as **"for"** or **"at"**.

Example Sentence: ```"Hey FishTank, What's on the menu``` **```today```** ```for``` **```dinner```**```?"```

The query process will take ```[ [ "menu" ], [ "for", "at" ] ]``` and take the first batch, **```today```** matching keyword **menu** and next detected keyword **for**.  
Second, the next batch is the **for** or **at**. Since we already know that it is **for** it'll just use **for** and detect that that is the last list in the query list and take from the keyword until the end, which will be **```dinner?```**.

Once the query process is done, it'll pass down those two as a list of ```["today", "dinner?"]``` as the ```args: list``` in the ```VoiceCommand.function()```.

## How to add commands
If you want to add commands, you'll have to know how ```VoiceCommand``` works, **please read the section above to fully understand ```VoiceCommand```.**

The voice assistant imports its command from .csv files inside of the [command list import](./Resources/command%20list%20import/) folder under [Resources](./Resources/). The parsing method will read from every .csv file and import them as commands.

Let's start by how to create your .csv file inside the command list import folder. Just open up any excel or sheets and name the first row correspondingly:
```
priority	type	function	command type	query list	import script name	trigger words
```

If you've read the explanation above, then this should all look very familiar. 
**Priority** is the integer.
**Type** is the command category.

**Function** however has two methods of utilization.  
1. You can input ```my_function_name``` to be called from the **import script name** module/script, or  
2. You can input ```"Because Seven Eight Nine."```. Putting a sentence in between **quotations** instead of calling a function it'll just speak whatever is in the quotation. 

If you've decided to go for the second method, then you can ignore the two attributes: **query list** and **import script name**

**Command Type** is Strict or Free. I've already explained it.

**Query List** will have a specific way of input. As specified in the [explanation](./#query-list) this is consist of a list of lists.

**```,```**: The Comma will be used to add an optional word, resulting in the import list looking like: ```at, in``` -> ```["at", "in"]```  
**```|```**: The Pipe will be the separator for adding an additional query word adding a new list: ```at,in```**|**```around,at``` -> ```["at", "in"], ["around", "at"]```

Theoretically, you can add as many pipes and commas as you can, but for the sake of the performance, please do not do that.

**Import Script Name** is the name of the python(.py) file inside the [ImportScript](./ImportScript/) folder, so something like ```my_script.py```

And the Trigger Words are words or sentences that will green-light a passing check inside the server. You may enter only one valid sentence but you can also use the same separator **```,```** to have additional ways of calling them.

For Example: ```what day is it, what is today, what day is today, what day is it today```

Your command will work under all the circumstances mentioned above.

# Making Voice Command Function
Once inside your python script, the first thing you should do is:
```
from Core.command import *
```
While this is optional technically, I strongly suggest doing it for many reasons.

After adding that in, then it's time to add in the function. Name it whatever you want, and remember to add the three parameters: spoken_sentence, command, and args.
```
def my_voice_command_function(spoken_sentence:str, command: VoiceCommand, args: list):
```
Inside, you can do anything. In this example, I'll show you what it is capable of:
```
from Core.command import *
import math

def power_two_numbers(spoken_sentence:str, command: VoiceCommand, args: list):
    first_number = int(args[0])
    second_number = int(args[1])

    result = math.pow(first_number, second_number)
    return_sentence = f"The power of {first_number} to the {second_number} is {result}"
    return (Result.SUCCESS, return_sentence)
```

The command.csv file would look like this.
```
priority    type	function	        command type	query list	import script name	    trigger words
1	    Math	power_two_numbers	Free	        of|to the	basic_commands	            The power of
```


