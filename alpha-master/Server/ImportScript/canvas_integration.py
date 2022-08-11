from canvasapi import Canvas; 
from canvasapi.course import Course; 
from enum import Enum; 
import datetime; 
from dateutil.relativedelta import relativedelta; 
import pytz; 
import requests; 
import Core.utility as util;  
from Core.server_system import *;
from icalendar import Calendar, Event; 
from Core.command import *; 
 
######################################################################
#####                       GLOBAL VARIABLES                     #####
######################################################################

SYSTEM_NAME = "CANVAS"; 

CANVAS_FOLDER_NAME = "Canvas"; 
CANVAS_CREDENTIAL_NAME = "credentials.mdat"; 

API_URL_TOKEN = "API_URL"; 
API_KEY_TOKEN = "API_KEY"; 

######################################################################
#####                       INIT FUNC & OBJ                      #####
###################################################################### 

def import_credentials(): 
    '''
    Parse credential file from {``CANVAS_FOLDER_NAME``} inside of {``CANVAS_FOLDER_NAME``}
    and return ``API_URL``(Canvas Instructor URL) and ``API_KEY``(User generated token)

    This method creates a new folder and a new credential file if there are none.  

    returns
    -------
    tuple
        ``(api_url, api_key)`` API URL and API KEY for use.
    or
    None
        if something goes wrong or there was no credential files.
    '''
    api_url = str(); 
    api_key = str(); 

    if path.mkdir_on_null(path.resources(CANVAS_FOLDER_NAME)):
        println(SYSTEM_NAME, f"{CANVAS_FOLDER_NAME} not found in the Resource folder. Creating one."); 

    credential_dir = path.resources(CANVAS_FOLDER_NAME, CANVAS_CREDENTIAL_NAME);  
    if path.make_file_on_null(credential_dir):
        print_warning(SYSTEM_NAME, f"Credential file not found, generating one. Please restart with them filled out to enable Canvas integration.");  
        file = open(credential_dir, "w");  
        file.write(f"{API_URL_TOKEN}=\n{API_KEY_TOKEN}=");  
        file.close(); 
        return; 
    try:
        file = open(credential_dir, 'r'); 
        for line in file.readlines():
            #Skip empty lines
            if len(line.strip()) <= 1: return;  
            
            split = line.split("="); 
            if len(split) == 1: 
                print_error(SYSTEM_NAME,"Error parsing credentials: No '=' found."); 
                return; 

            if line.startswith(API_URL_TOKEN): 
                api_url = split[1]; 
            elif line.startswith(API_KEY_TOKEN):
                api_key = split[1]; 

        return (api_url, api_key); 
    except Exception as e:
        print(e); 
        print_error(SYSTEM_NAME,"Something went wrong while parsing the credentials. Disabling canvas integration."); 


class Courses(object):
    def __init__(self):
        self.courses = self.__get_valid_classes(); 
        self.update_date = util.get_date(); 

    def get_classes(self):
        if self.update_date <= util.get_past_date(5):
            self.courses = self.__get_valid_classes(); 
            self.update_date = util.get_date(); 
        return self.courses; 

    @classmethod
    def __get_valid_classes(cls, **keyword) -> list[Course]:
        valid_courses = list[Course]();  
        utc = pytz.UTC; 
        classes:list[Course] = CANVAS.get_current_user().get_courses(**keyword);  
        for course in classes:
            current_date = datetime.datetime.now();   
            #Class not applicable, skipping. 
            if course.start_at == None: continue;   
            # if the class has not even started yet then it is not valid.
            if utc.localize(current_date) < course.start_at_date: continue;  
            end_date = None; 
            if course.end_at == None:
                #If there is no end date, then I'll assume that the courses end after 6 months.
                end_date = utc.localize(current_date + relativedelta(months = 6));  
            else: 
                end_date = course.end_at_date;  
            #If the class is already over, then it is not applicable
            if utc.localize(current_date) >= end_date: continue;  
            valid_courses.append(course);   
        return valid_courses;  


######################################################################
#####                       CANVAS + COURSE                      #####
###################################################################### 

API_URL, API_KEY = import_credentials(); 
CANVAS = Canvas(API_URL, API_KEY); 
COURSES = Courses(); 


######################################################################
#####                       COURSE SCHEDULE                      #####
###################################################################### 


class Day(Enum): 
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday" 
    

def day_to_string(day:Day) -> str:
    if day == Day.MONDAY: return "Monday"; 
    elif day == Day.TUESDAY: return "Tuesday";  
    elif day == Day.WEDNESDAY: return "Wednesday";  
    elif day == Day.THURSDAY: return "Thursday";  
    elif day == Day.FRIDAY: return "Friday";  
    elif day == Day.SATURDAY: return "Saturday";  
    elif day == Day.SUNDAY: return "Sunday";  
    raise Exception("The given day doesn't exist. I don't know how this even happens."); 


def parse_day(day) -> Day:
    '''
    Parse into Day object using two char like "MO" for Monday
    or
    it parses from "monday" 
    '''
    if len(day) > 4:
        day = day.lower().strip(); 
        if 'monday' in day: return Day.MONDAY; 
        elif 'tuesday' in day: return Day.TUESDAY; 
        elif 'wednesday' in day: return Day.WEDNESDAY; 
        elif 'thursday' in day: return Day.THURSDAY; 
        elif 'friday' in day: return Day.FRIDAY; 
        elif 'saturday' in day: return Day.SATURDAY; 
        elif 'sunday' in day: return Day.SUNDAY; 
        else: return None; 
    
    if day == "MO": return Day.MONDAY;  
    elif day == "TU": return Day.TUESDAY;  
    elif day == "WE": return Day.WEDNESDAY;  
    elif day == "TH": return Day.THURSDAY;  
    elif day == "FR": return Day.FRIDAY;  
    elif day == "SA": return Day.SATURDAY;  
    elif day == "SU": return Day.SUNDAY;  
    else:
        return None; 

def parse_days(day_list) -> list[Day]:
    return_list = []; 
    for day in day_list: 
        return_list.append(parse_day(day)); 
    return return_list;  

def get_relative_day(date) -> Day:
    ''' Return Day object with param of string that matches either "Today", "Tomorrow", or "Yesterday"'''
    date = date.lower();  
    day = datetime.date.today(); 
    singleday = datetime.timedelta(days=1); 
    if "today" in date:
        pass; 
    elif "tomorrow" in date:
        day += singleday; 
    elif "yesterday" in date:
        day -= singleday; 
    else:
        return None; 

    day_string = day.strftime('%A'); 
    two_char = day_string.upper()[:2]; 
    return parse_day(two_char); 

    

class CourseSchedule(object):  

    def __init__(self, title, start:datetime.datetime, end:datetime.datetime, days):
        self.title = title; 
        self.start:datetime.datetime = start; 
        self.end:datetime.datetime = end; 
        self.days:list[Day] = parse_days(days); 
    
    def get_days_values(self):
        return [day.value for day in self.days]; 

    def __str__(self):
        days = [day_to_string(day) for day in self.days]; 
        days_string = util.localize_items(days); 
        return_string =  f'{self.title} starts '; 
        return_string += f'from {self.start.strftime("%I:%M %p")} '; 
        return_string += f'to {self.end.strftime("%I:%M %p")} '; 
        return_string += f'every {days_string}.'; 
        return return_string; 
    
    def start_readable(self):
        return util.datetime_to_readable(self.start); 

    def end_readable(self):
        return util.datetime_to_readable(self.end); 

    def is_in_between(self, time:datetime.datetime, day:Day = None):
        #00:00 format
        start, _ = VoiceCommand.parse_time(self.start); 
        end, _ = VoiceCommand.parse_time(self.end); 
        curr, _ = VoiceCommand.parse_time(time);  

        if day != None:
            if day not in self.days: return False; 
        if curr >= start and curr <= end:
            return True; 
        else:
            return False;    
    
    def has_words_in_title(self, words:list):
        total_count = len(words); 
        for word in words:
            word = word.strip().lower(); 
            title = self.title.lower();  
            if word == "start" or word == "end":
                continue;  
            if word not in title:
                print("No match ", word); 
                print('matching', title); 
                return False;  
        #match_list = [word for word in words if word.strip().lower() in self.title.lower()]; 
        #return total_count == len(match_list); 
        return True; 

    def is_in_day(self, day:Day):
        return day in self.days;  
    
    def __lt__(self, other): 
        condition1 = self.start < other.start;  
        return condition1; 
    def __le__(self, other):
        condition1 = self.start <= other.start;  
        return condition1; 
    def __eq__(self, other):
        condition1 = self.start == other.start;  
        return condition1; 
    def __ne__(self, other):
        condition1 = self.start != other.start;  
        return condition1; 
    def __gt__(self, other):
        condition1 = self.start > other.start;  
        return condition1; 
    def __ge__(self, other):
        condition1 = self.start >= other.start;  
        return condition1; 

###########################################################################
#####                 COURSES CLASS & OTHER FUNCTIONS                 #####
###########################################################################

def get_course_schedule(course): 
    try: 
        ics_link = course.calendar['ics']; 
    except:  
        return []; 
    
    file = util.get_file("course_schedule_" + str(course.id), ics_link, "rb"); 
    if file == None: return [];  
 
    schedule:Calendar = Calendar.from_ical(file.read());  
    schedules = []; 

    for component in schedule.walk():
        if component.name != "VEVENT": continue;  
        try:
            summary = component.get('summary'); 
            start_time = component.decoded('dtstart'); 
            end_time = component.decoded('dtend');  
            rrule = component.get("rrule");     
            days = rrule['BYDAY']; 
        except:
            #Not the right type we're looking for. 
            continue; 
        schedules.append(CourseSchedule(summary, start_time,end_time, days)); 
    return schedules; 

def get_course_schedules(courses) -> list[CourseSchedule]:
    schedules = []; 
    for course in courses:
        [schedules.append(schedule) for schedule in get_course_schedule(course)]; 
    return schedules;  


######################################################################
#####                 VOICE ASSISTANT FUNCTIONS                  #####
######################################################################  

def get_course_in_lab_via_time(spoken_sentence:str, command: VoiceCommand, args: list, **extra):
    #what class is at --   
    try:
        specified_time, time = VoiceCommand.parse_time(args[0]); 
    except Exception as e:
        print(e)
        return (Result.SUCCESS, "Please say a valid time such as 12:30 a.m."); 
    if specified_time == None:
        return (Result.SUCCESS, "Please specify the exact time by saying either a.m. or p.m.");  
    
    schedules = get_course_schedules(COURSES.get_classes()); 
    schedules = [schedule for schedule in schedules if schedule.is_in_between(time)]; 
    schedules.sort(); 

    time_datetime = time;  
    time_string = time_datetime.strftime("%I:%M %p"); 

    count = len(schedules);  
    if count == 0:
        return (Result.SUCCESS, f"There are no classes at {time_string}."); 
    elif count == 1:
        message = f"At {time_string}, "; 
        message += f"{schedules[0].title} takes place from "; 
        message += f"{schedules[0].start_readable()} until {schedules[0].end_readable()}."; 
        return (Result.SUCCESS, message); 
    else:
        message = f"There are {count} classes at {time_string}. "; 
        schedule_messages = []; 
        for schedule in schedules:
            sch_msg = f"At {time_string}, "; 
            sch_msg += f"{schedule.title} takes place from "; 
            sch_msg += f"{schedule.start_readable()} until {schedule.end_readable()}"; 
            schedule_messages.append(sch_msg); 
        message += util.localize_items(schedule_messages); 
        return (Result.SUCCESS, message + '.');  

#PRIORITY 2
def get_course_in_lab_via_time_date(spoken_sentence:str, command: VoiceCommand, args: list, **extra):
    #what class is at --   
    try:
        specified_time, relative_date, time = VoiceCommand.parse_time_date(args[0]); 
    except Exception as e:
        print(e)
        return (Result.FAIL, ""); 
 
    day = get_relative_day(relative_date); 
    print("E:", day); 
    if day == None:
        return (Result.FAIL, ""); 

    schedules = get_course_schedules(COURSES.get_classes()); 
    schedules = [schedule for schedule in schedules if schedule.is_in_between(time, day)]; 
    schedules.sort(); 

    count = len(schedules); 
    if count == 0:
        return (Result.SUCCESS, f"There are no classes at {args[0]}."); 
    elif count == 1:
        message = f"At {args[0]}, "; 
        message += f"{schedules[0].title} takes place every {str(day.value)} from "; 
        message += f"{schedules[0].start_readable()} until {schedules[0].end_readable()}."; 
        return (Result.SUCCESS, message); 
    else:
        message = f"There are {count} classes at {args[0]}. "; 
        schedule_messages = []; 
        for schedule in schedules:
            sch_msg = f"At {args[0]}, "; 
            sch_msg += f"{schedule.title} takes place every {str(day.value)} from "; 
            sch_msg += f"{schedule.start_readable()} until {schedule.end_readable()}"; 
            schedule_messages.append(sch_msg); 
        message += util.localize_items(schedule_messages); 
        return (Result.SUCCESS, message + '.'); 

def get_courses_via_relatve_date(spoken_sentence:str, command: VoiceCommand, args: list, **extra):
    #what classes are >there< "today".
     
    day = get_relative_day(args[0]);  
    if day == None:
        return (Result.FAIL, "");  
    
    schedules = get_course_schedules(COURSES.get_classes()); 
    schedules = [schedule for schedule in schedules if schedule.is_in_day(day)]; 
    schedules.sort(); 

    count = len(schedules); 
    if count == 0:
        return (Result.SUCCESS, f"There are no classes {day.value}."); 
    else:
        message = f"There are {count} classes {day.value}. "; 
        schedule_messages = []; 
        for schedule in schedules:
            sch_msg = f"{day.value}, "; 
            sch_msg += f"{schedule.title}, at {schedule.start_readable()}"; 
            schedule_messages.append(sch_msg); 
        message += util.localize_items(schedule_messages); 
        return (Result.SUCCESS, message + '.'); 

def get_courses_via_date(spoken_sentence:str, command: VoiceCommand, args: list, **extra):
    #what classes are >on< "Mondays".
     
    day_string = args[0].strip(); 
    day:Day = parse_day(day_string);  
    if day == None:
        return (Result.FAIL, "");   
    
    schedules = get_course_schedules(COURSES.get_classes()); 
    schedules = [schedule for schedule in schedules if schedule.is_in_day(day)]; 
    schedules.sort(); 

    count = len(schedules); 
    if count == 0:
        return (Result.SUCCESS, f"There are no classes {day.value}."); 
    else:
        message = f"There are {count} classes {day.value}. "; 
        schedule_messages = []; 
        for schedule in schedules:
            sch_msg = f"{day.value}, "; 
            sch_msg += f"{schedule.title}, at {schedule.start_readable()}"; 
            schedule_messages.append(sch_msg); 
        message += util.localize_items(schedule_messages); 
        return (Result.SUCCESS, message + '.'); 

def get_course_time_via_description(spoken_sentence:str, command: VoiceCommand, args: list, **extra):
    #when >does/is< intro to networking |start|? '|' = irrelevant 
    descriptions = args[0].split(' '); 
    
    schedules = get_course_schedules(COURSES.get_classes()); 
    schedules = [schedule for schedule in schedules if schedule.has_words_in_title(descriptions)]; 
    schedules.sort();  
    count = len(schedules); 
    if count == 0:
        # *** implement further elaboration so it can have more than one "when" trigger words in other scripts
        return (Result.SUCCESS, f"Sorry I couldn't find any class named {args[0]}."); 
    if count == 1:
        schedule = schedules[0]; 
        message = f"{schedule.title} takes place from {schedule.start_readable()} "; 
        message += f"to {schedule.end_readable()} every {util.localize_items(schedule.get_days_values())}. "; 
        return (Result.SUCCESS, message + '.'); 
    else:
        message = f"I found {count} classes by the descriptions of {args[0]}. "; 
        schedule_messages = []; 
        for schedule in schedules: 
            message_sub = f"{schedule.title} takes place from {schedule.start_readable()} "; 
            message_sub += f"to {schedule.end_readable()} every {util.localize_items(schedule.get_days_values())}"; 
            schedule_messages.append(message_sub); 
        message += util.localize_items(schedule_messages); 
        return (Result.SUCCESS, message + '.'); 


#def get_course_in_lab_now(spoken_sentence:str, command: VoiceCommand, args: list, **extra):
