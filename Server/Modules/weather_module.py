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


async def getweather(location):
    # declare the client. format defaults to metric system (celcius, km/h, etc.)
    client = python_weather.Client(format=python_weather.IMPERIAL); 

    # fetch a weather forecast from a city
    weather = await client.find(location); 

    #print("current: ", weather.current.date, weather.c); 

    # returns the current day's forecast temperature (int)
    print(weather.current.temperature); 

    # get the weather forecast for a few days
    for forecast in weather.forecasts:
        print(str(forecast.date), forecast.sky_text, forecast.temperature); 

    # close the wrapper once done       
    await client.close();               

def get_irvine_weather():               
    loop = asyncio.get_event_loop();    
    loop.run_until_complete(get_current_weather()); 
    global current_weather;             
    return current_weather;             

def get_weather(location):  
    loop = asyncio.get_event_loop(); 
    loop.run_until_complete(get_current_weather(location)); 
    global current_weather; 
    return current_weather; 