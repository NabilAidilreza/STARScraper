import re
import json
from datetime import datetime,timedelta
from ntu_extract_timetable import create_timetable_list

#! FUNCTIONS FOR TELEGRAM BOT #

### Info Gathering Functions ### 

def compile_mods(data,start_date):
    SD = start_date.split("/")
    startday = datetime(int(SD[-1]), int(SD[1][1]) if SD[1][0] == "0" else int(SD[1]), int(SD[0]), 0, 0, 0) 
    referenceDay = {'Mon':0,'Tue':1,'Wed':2,'Thu':3,'Fri':4,'Sat':5}  
    # Generates a dictionary of key information for easy access #
    sem_dict = {}
    for week in data[1:]:
        for event in week:
            mod_code = event[0]
            # Add event timeline (daily info) #
            current_event_week = event[14].split()[1]
            current_event_day = event[11]
            # Calculate Date #
            if len(current_event_week) == 4:
                date = startday + timedelta(days=(7*(int(current_event_week[2:4])))+referenceDay[current_event_day])
            else:
                if int(current_event_week[2]) >= 8:
                    date = startday + timedelta(days=(7*(int(current_event_week[2])))+referenceDay[current_event_day])
                else:
                    date = startday + timedelta(days=(7*(int(current_event_week[2])-1))+referenceDay[current_event_day])
            date = date.strftime("%d-%m-%Y")
            if mod_code not in sem_dict:
                # Initialize mod #
                sem_dict[mod_code] = {"Course_Info":{},"Timeline":{}}
                # Add revelent info #
                sem_dict[mod_code]["Course_Info"] = {"Name":event[1],"AU":event[2],"Status":event[7],"Type":event[3],"Index":event[6],"Grp":event[10],"Venue":event[13],"Finals":event[15]}
                if current_event_week not in sem_dict[mod_code]["Timeline"]:
                    sem_dict[mod_code]["Timeline"][current_event_week] = {current_event_day:{event[12]:[event[9],event[13],date]}}
                else:
                    if current_event_day not in sem_dict[mod_code]["Timeline"][current_event_week]:
                        sem_dict[mod_code]["Timeline"][current_event_week][current_event_day] = {event[12]:[event[9],event[13],date]}
                    else:
                        sem_dict[mod_code]["Timeline"][current_event_week][current_event_day].update({event[12]:[event[9],event[13],date]})
            else:
                if current_event_week not in sem_dict[mod_code]["Timeline"]:
                    sem_dict[mod_code]["Timeline"][current_event_week] = {current_event_day:{event[12]:[event[9],event[13],date]}}
                else:
                    if current_event_day not in sem_dict[mod_code]["Timeline"][current_event_week]:
                        sem_dict[mod_code]["Timeline"][current_event_week][current_event_day] = {event[12]:[event[9],event[13],date]}
                    else:
                        sem_dict[mod_code]["Timeline"][current_event_week][current_event_day].update({event[12]:[event[9],event[13],date]})
    return sem_dict

def print_table(final_data):
    for i in range(len(final_data)):
        print("\nWeek {}\n".format(i))
        for mods in final_data[i]:
            print(mods)

def pretty_print(mod_dict):
    pretty = json.dumps(mod_dict, indent=4)
    print(pretty)

### Getters For NTU Module Info (TELEGRAM BOT) ###

# ALL MUST RETURN STRING #
def get_all_mods(ldict):
    result = "Your modules this semester: \n\n"
    for mod in ldict:
        result += get_course_info(ldict,mod) + "\n\n"
    return result

def get_course_info(ldict,course_code):
    if course_code not in ldict:
        return "No such module"
    else:
        result = course_code + "\n"
        course_info = ldict[course_code]["Course_Info"]
        for key,value in course_info.items():
            result += key + ": " + value + "\n"
        return result

# Returns todays agenda #
def get_today(ldict,test_date):
    lst = []
    for mod in ldict:
        timeline = ldict[mod]["Timeline"]
        for week in timeline:
            days = timeline[week]
            for day in days:
                key = list(days[day].keys())[0]
                if days[day][key][2] == test_date:
                    type = days[day][key][0]
                    venue = days[day][key][1]
                    lst.append([mod,week,day,key,type,venue])
    if lst == []:
        return "No classes today on " + test_date
    result = "Today's date: " + test_date + " - " + lst[0][1] + " - " + lst[0][2] + "\n"
    result += "Agenda: \n"
    lst.sort(key=lambda lst: lst[3])
    for ele in lst:
        result += "{}    {:<10}{:<10}{}\n".format(ele[3],ele[0],ele[4],ele[5])
    return result

# Returns given week agenda #
def get_weekly(ldict,week_num):
    lst = []
    if week_num == 0:
        return "Error occured when processing data."
    week = "Wk"+str(week_num)
    j = {'Fri': 4, 'Thu': 3, 'Wed': 2, 'Mon': 0, 'Tue': 1}
    for mod in ldict:
        timeline = ldict[mod]["Timeline"]
        if week in timeline:
            for day in timeline[week]:
                for key,value in timeline[week][day].items():
                    lst.append([mod,j[day],key,value])
    t = {v: k for k, v in j.items()}
    # Copy t to d
    j.clear()
    j.update(t)
    # Remove t
    del t
    lst.sort(key=lambda lst: lst[2])
    lst.sort(key=lambda lst: lst[1])
    for i in range(len(lst)):
        num = lst[i][1]
        lst[i][1] = j[num]
    result = week + "\n"
    prev_day = lst[0][1]
    result += prev_day + ": \n"
    result += "    Date: " + lst[0][3][2] + "\n"
    curr_day = ""
    k = 0
    while prev_day != "Fri" and k < len(lst):
        curr_day = lst[k][1]
        if curr_day != prev_day:
            result += "\n" + curr_day + ": \n"
            result += "    Date: " + lst[k][3][2] + "\n"
            prev_day = curr_day
        toadd = "    {} => {} | {} | {}\n".format(lst[k][0],lst[k][2],lst[k][3][0],simplify_venue(lst[k][3][1]))
        result += toadd
        k += 1
    return result

# Return week num and day of given date #
def check_what_week_day(timeline,test_date):
    #td = test_date.split("/")
    #test_date_datetime = datetime(int(td[-1]), int(td[1][1]) if td[1][0] == "0" else int(td[1]), int(td[0]), 0, 0, 0)   
    for i,week in enumerate(timeline):
        for j,day in enumerate(week):
            if test_date == day:
                return i+1,j
    return 0

# Generate Timeline
# Return sem week dates #
def generate_timeline(start_date):
    timeline = []
    num_of_weeks = 14 # Same for every semester
    sd = start_date.split("/")
    startday = datetime(int(sd[-1]), int(sd[1][1]) if sd[1][0] == "0" else int(sd[1]), int(sd[0]), 0, 0, 0)   
    for i in range(num_of_weeks):
        week = []
        if i == 0:
            continue # Skip the first iteration (week 0)
        elif i >= 8:
            pass
        else:
            i = i-1
        for j in range(6): # Monday to Saturday
            date = startday + timedelta(weeks=i,days=j)
            week.append(date.strftime("%d/%m/%Y"))
        timeline.append(week)
    return timeline

# Display timeline #
def print_timeline(timeline):
    for week in timeline:
        week_string = ""
        for day in week:
            week_string += day + " | "
        print(week_string)

# Simplify venue #
def simplify_venue(venue):
    pattern = r'\[(.*?)\]'
    terms = re.split(pattern, venue)
    if len(terms) <= 2:
        return venue
    abbrev = terms[0]
    full = terms[1]
    pattern = r'\((.*?)\)'
    area = re.search(pattern, full).group(0)
    if "LHN" in abbrev or "LHS" in abbrev: # Means at the Arc
        tr = abbrev.split("-")[1]
        return tr + " " + area
    elif "LT" in abbrev: # Its a LT
        return abbrev + " " + area
    elif len(abbrev.split("-")) >= 3: # A lab of sorts
        return abbrev + " " + area
    else:
        # Should be a TR
        return abbrev + " " + area

def combine_NTU_dict(ldict, timeline, file_name):
    final_dict = {}
    final_dict["file_name"] = file_name # String
    final_dict["timeline"] = timeline # List
    final_dict["mods"] = ldict # Dict
    return final_dict

def test():
    test_data = create_timetable_list("STARS_NABIL.html")
    test_dict = compile_mods(test_data,"15/03/2025")
    #timeline = generate_timeline("15/03/2025")
    print(test_dict)
    #print_timeline(timeline)



