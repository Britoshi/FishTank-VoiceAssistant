import python_weather; 
import asyncio;

current_weather = str(); 

async def get_current_weather(location: str = "Irvine") -> str: 
    client = python_weather.Client(format=python_weather.IMPERIAL); 
    weather_info = await client.find(location); 

    weather = weather_info.current;    
    global current_weather; 
    current_weather = "It is currently " + str(weather.temperature) + " degrees, " + weather.sky_text + " outside in " + location;  
    
    await client.close()


async def get_weather(location):
    # declare the client. format defaults to metric system (celsius, km/h, etc.)
    client = python_weather.Client(format=python_weather.IMPERIAL); 

    # fetch a weather forecast from a city
    weather_info = await client.find(location);  

    weather = weather_info.current;    
    global current_weather; 
    current_weather = "It is currently " + str(weather.temperature) + " degrees, " + weather.sky_text + " outside in " + location;  
    
    # close the wrapper once done       
    await client.close();               

def get_irvine_weather():         
    asyncio.set_event_loop(asyncio.new_event_loop()) 
    asyncio.get_event_loop().run_until_complete(get_current_weather());   
    global current_weather;             
    return current_weather;             

def get_weather(location):     
    asyncio.set_event_loop(asyncio.new_event_loop())
    try:
        asyncio.get_event_loop().run_until_complete(get_current_weather(location));  
    except:
        return ("Sorry, I don't know where that is."); 
        
    global current_weather; 
    return current_weather; 