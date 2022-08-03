import Core.utility as util;
from Core.server_system import *;  

USERLIST_PATH = util.PARENT_DIR + "/Resources/DiscordUserList.mdat"; 

def get_file(type):
    if not util.file_exists(USERLIST_PATH):
        println("Discord API", f"User List not found. Creating one..."); 
        open(USERLIST_PATH, 'w').close(); 
    return open(USERLIST_PATH, type); 

def parse_users(lines):
    user_list = list(); 
    for line in lines:
        if len(line.strip()) == 0: continue; 
        user_list.append(line.replace("\n", "")); 
    return user_list; 

class DiscordServerAPI:
    def __init__(self):
        file = get_file("r"); 
        self.approved_user_list = parse_users(file.readlines()); 
        file.close(); 
        println("Discord API", "API loaded Successfully."); 

    def users_to_list(self):
        users = ""; 
        for user in self.approved_user_list:
            users += user + '|'; 
        return users; 

    def users_to_file_format(self):
        text = ""; 
        for user in self.approved_user_list:
            text += user + "\n"; 
        return text; 

    def add_user(self, user):
        file = get_file("w"); 
        if user not in self.approved_user_list:
            println("Discord API", "The given user is already an approved user.")
            self.approved_user_list.append(user); 
        println("Discord API", f"Successfully registered user: {user}."); 
        file.write(self.users_to_file_format() + user); 
        file.close(); 