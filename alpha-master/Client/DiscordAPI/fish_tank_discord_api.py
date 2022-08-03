import discord; 
import os;  
import asyncio; 
import time;

class DiscordInfo:
    def __init__(self): 
        self.channel_id:int = -1; 
        self.authorized_user_list = list(); 
        self.output_message = None; 
        self.token = None;  
        
        self.network_function:function = None; 
        self.add_function:function = None;  

    def add_user(self, user):
        if len(user.strip()) < 1:
            return; 
        self.authorized_user_list.append(user);  
    
    def approve_new_user(self, user):
        self.add_user(user); 
        self.add_function(user);  

CLIENT = discord.Client(); 
INFO = DiscordInfo(); 

class DiscordBot(object):  
    def __init__(self): 
        self.client = CLIENT;  
        self._channel = None; 
        self.info = INFO;  

    def run(self, token):
        self.client.run(token); 


    def get_channel(self):
        if self._channel == None:
            self._channel = self.client.get_channel(self.info.channel_id); 
        return self._channel;  

    def write_message(self, message):  
        self.info.output_message = message;  


@CLIENT.event
async def on_ready():
    print('We have logged in as {0.user}'.format(CLIENT)); 

@CLIENT.event
async def on_message(message:discord.Message): 
    if message.author == CLIENT.user:
        return 

    if type(message.channel) != discord.TextChannel: return;  
    if message.channel.id != INFO.channel_id: return; 

    msg = str(message.content).lower(); 

    if msg.startswith('fish tank') or msg.startswith('fishtank'):
        
        if str(message.author.id) not in INFO.authorized_user_list: 
            await message.channel.send("You're not authorized. Please contact anyone in charge."); 
            return; 

        #TEMP
        if "authorize user " in msg:
            user = msg.split("user ")[1].strip()
            user_id = user[2:-1];  
            INFO.approve_new_user(user_id); 
            await message.channel.send(f"{user} has been authorized."); 
            return; 

        await fishtank_speech_handler(message);  

async def fishtank_speech_handler(message: discord.Message):

    INFO.network_function(message.content);    

    start_time = time.time(); 
    while INFO.output_message == None:
        curr_time = time.time(); 
        if curr_time - start_time > 30:
            print("Something went horribly wrong in the messaging process. Ignoring..."); 
            return; 
        continue; 
    await message.channel.send(INFO.output_message); 
    INFO.output_message = None; 
