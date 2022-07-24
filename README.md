
# 🐠 FISHTANK VOICE ASSISTANT 🐟
Welcome to documention of the FishTank Voice Assistant. This is a very scuffed documention
of how the voice assistant work.
FishTank is created for the intention of it being use in the Computer Science Laboratory at the Concordia University Irvine. If used in a foreign environment results may vary.

Fishtank Voice Assistant is very modular and easily customizable. Just by adding one line in a csv file you can create a new command for the voice assistant.
If you're here to learn how to add commands, goto this 
[page on how to add new commands](./alpha-master/Server#adding-new-commands). 


## How does it work?
The voice assistant works by having two programs running in parallel with the 
[server](./alpha-master/Server/)
and the 
[client](./alpha-master/Client/).  
Once the server is ready to go and client is also up and running, the server first sends a 
[packet]
with a 
request 
[header]
and
[body]
to the client.
The client will then make sure the request is valid and if it is valid, then it will begin processing the network request. If request is made for picking up speech, the client will listen to the default microphone and pick up words using Google's Speech Recognition and return matched words back to the server with the return header and spoken sentence.  
Once the return header reaches the server, the server will then go through it's database to see if the spoken sentence can be used.  

There are two layers as of current.  
1. from spoken sentence, the server will look for the keyword "fishtank". If the server was able to pick up fishtank, then it'll go to the server and send another request to the client to see if what the speaker wants from the voice assistant. The client will return a spoken sentence upon success which brings it to the second layer.  
2. from the second spoken sentence the server will then search through its database and response correspondingly. 



# Configuration
Configuration file will be automatically generated if there is no 'properties.cfg' present
in the root directory. This is currently more of a network configuration rather than anything else.

This is what the config file should look like.
```
#FishTank Voice Assistant Configuration Version 0.1
HOST_IP=192.168.1.101
PORT=42069
```
As of config file format version 0.1, there are only two properties. They are very self
explanatory and if you don't know what those are, then you've never played Minecraft before.
 

# Networking
## Connecting
It's very self explanatory but the server and the client will read the network information from the configuration file and host/connect to the given address and port.

## Communication
I've made it pretty straight forward on how the server communicates to the client by implementing my own [**tokening system**](.#tokens). But before explaining what tokenization is, I have to first explain the basic networking behind it. 

The server and client uses the built in module 'socket' to send packets to one another.  
The client will have a constant loop in its system that is on a stand by for any packets that may get send towards it. Once the server sends a packet, it'll process it using the given [tokens](.#tokens) and send a appropriate packet back to the server.

## Tokens
Tokens are strings/bytes that dictates what the server/client will do with the packet. In each of the **utility** script in both the client and server, they'll have a method named ```get_token``` method inside. 

The ```get_token(token_string:str)``` method return a matching token to the ```token_string``` variable from reading the file [TOKEN.txt in Client](./alpha-master/Client/Resources/TOKEN.txt) or [TOKEN.txt in Client](./alpha-master/Server/Resources/TOKEN.txt).  

Inside of the file should look something like this:
```
KEY_TOKEN, >>PACKET<<
TIMEOUT, TIMEOUT
REQUEST_SENTENCE, *FUNC*ARGS:NETWORK_REQUEST_SENTENCE
RETURN_REQUEST_SENTENCE, *ARGS:RETURN_REQUEST_SENTENCE
STOP_SIGNAL, *FUNC:NETWORK_EXIT
CLIENT_SPEAK, *FUNC*ARGS:NETWORK_SPEAK
```
For those who are used to tokenization, yes this is very confusing since tokenization usually revolves around commas, but you'll have to bear with me since I don't even know why I named them tokens.

**Each line should have a single comma no more or no less.**  
The left side should be the ```token_string``` mentioned above. It is the string that you'll be using inside code and not something the server or the client will know. I don't think I have to say this, but make sure there are no duplicates.

The right side is what the server/client will read and comprehend. To explain further, I'll now explain how the server and client communicates.

A typical spoken sentence request will look like this:  
```
>>PACKET<<|*FUNC*ARGS:NETWORK_REQUEST_SENTENCE|TIMEOUT=10
```
### Header
With each packet received, the server/client will split them using the pipes that look like "**```|```**" found on your keyboard next to "]".  
As you can see, ```>>PACKET<<``` matches the ```KEY_TOKEN```. That is the header shared between the two program to know that it is receiving packet from the each other and not any other foreign entity.

### Body
Now that we know that the packet is valid, we'll proceed to read the second pipe: **the body**.  
The body is the right side of the comma shown above in the TOKEN.txt example.  
It's pretty clear that it is the ```REQUEST_SENTENCE``` from the TOKEN.txt, matching ```*FUNC*ARGS:NETWORK_REQUEST_SENTENCE```.
##### What are those **\*FUNC** and **\*ARGS**?
**\*FUNC** indicates that what ever written in the body after the colon is a function that can run. Once the server sends the packet above, the client will take the body, ```NETWORK_REQUEST_SENTENCE``` and check to see if they have any matching function named ```network_request_sentence``` inside the client. Once it has found it it'll run the specific function. All the network function can be found in the [client_runner.py](./alpha-master/Client/client_runner.py) under the section ```#### NETWORK METHODS SEND BACK METHODS #####```  
**This will be changed in the future if the network traffic becomes heavier than it currently is.**  

**\*ARGS** indicates that the there will be a third pipe separating a new section dedicated to reading the arguments.  
As given in the packet example above, the argument is ```TIMEOUT=10```. Inside the client there's a function that parses the arguments automatically for use which then the contents will be passed into the functions, in this case ```network_request_sentence``` as the parameter of the function. 

You can add more arguments by adding commas. For example to add a second argument:
```>>PACKET<<|*FUNC*ARGS:EXAMPLE_FUNCTION|```**```EXAMPLE_ARGUMENT_ONE=1,EXAMPLE_ARGUMENT_TWO=2```**

In each *FUNC functions, they will send a packet back to the open socket, back to the server with the correct header of course, but with ```RETURN_REQUEST_SENTENCE``` body and a arguemnt which will be the content of the spoken sentence.

That wraps up on how the communication is taken between the two machines. Very straight forward I'd way. The machines check on each other on which caller to use using the ```get_token``` function.

#### How to add more?
The server and the client automatically downloads the newest information they can find of the TOKEN.txt and updates them. How to access said file... uh, you gotta come to me because I honestly didn't think anyone would dig this deep. Even if you add more manually, it'll just revert back so good luck.

But anything else other than that feel free to download and edit the script and add your own functionality to it, but this is not as modular as the voice commands.




