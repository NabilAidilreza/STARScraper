import json
import re
from datetime import timedelta

try:
    from ntu_extract_timetable import (
        create_timetable_list,
        teaching_week_start,
    )
except ImportError:
    from .ntu_extract_timetable import (
        create_timetable_list,
        teaching_week_start,
    )

# FUNCTIONS FOR TELEGRAM BOT #

### Info Gathering Functions ### 

def compile_mods(data, start_date):
    referenceDay = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5}
    # Generates a dictionary of key information for easy access #
    sem_dict = {}
    for week in data[1:]:
        for event in week:
            mod_code = event[0]
            # Add event timeline (daily info) #
            current_event_week = event[14].split()[1]      # e.g. "Wk3"
            current_event_day = event[11]
            # Calculate Date (recess week accounted for by teaching_week_start) #
            week_num = int(current_event_week[2:])
            date = teaching_week_start(week_num, start_date) + timedelta(days=referenceDay[current_event_day])
            date = date.strftime("%d/%m/%Y")
            if mod_code not in sem_dict:
                # Initialize mod #
                sem_dict[mod_code] = {"Course_Info": {}, "Timeline": {}}
                # Add revelent info #
                sem_dict[mod_code]["Course_Info"] = {"Name": event[1], "AU": event[2], "Status": event[7], "Type": event[3], "Index": event[6], "Grp": event[10], "Venue": event[13], "Finals": event[15]}
                if current_event_week not in sem_dict[mod_code]["Timeline"]:
                    sem_dict[mod_code]["Timeline"][current_event_week] = {current_event_day: {event[12]: [event[9], event[13], date]}}
                else:
                    if current_event_day not in sem_dict[mod_code]["Timeline"][current_event_week]:
                        sem_dict[mod_code]["Timeline"][current_event_week][current_event_day] = {event[12]: [event[9], event[13], date]}
                    else:
                        sem_dict[mod_code]["Timeline"][current_event_week][current_event_day].update({event[12]: [event[9], event[13], date]})
            else:
                if current_event_week not in sem_dict[mod_code]["Timeline"]:
                    sem_dict[mod_code]["Timeline"][current_event_week] = {current_event_day: {event[12]: [event[9], event[13], date]}}
                else:
                    if current_event_day not in sem_dict[mod_code]["Timeline"][current_event_week]:
                        sem_dict[mod_code]["Timeline"][current_event_week][current_event_day] = {event[12]: [event[9], event[13], date]}
                    else:
                        sem_dict[mod_code]["Timeline"][current_event_week][current_event_day].update({event[12]: [event[9], event[13], date]})
    return sem_dict

def print_table(final_data):
    for i in range(len(final_data)):
        print(f"\nWeek {i}\n")
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
        result += get_course_info(ldict, mod) + "\n\n"
    return result

def get_course_info(ldict, course_code):
    if course_code not in ldict:
        return "No such module"
    else:
        result = course_code + "\n"
        course_info = ldict[course_code]["Course_Info"]
        for key, value in course_info.items():
            result += key + ": " + value + "\n"
        return result

# Returns todays agenda #
def get_today(ldict, test_date):
    lst = []
    for mod in ldict:
        timeline = ldict[mod]["Timeline"]
        for week in timeline:
            days = timeline[week]
            for day in days:
                for key, value in days[day].items():
                    if value[2] == test_date:
                        lst.append([mod, week, day, key, value[0], value[1]])
    if lst == []:
        return "No classes today on " + test_date
    result = "Today's date: " + test_date + " - " + lst[0][1] + " - " + lst[0][2] + "\n"
    result += "Agenda: \n"
    lst.sort(key=lambda lst: lst[3])
    for ele in lst:
        result += f"{ele[3]}    {ele[0]:<10}{ele[4]:<10}{ele[5]}\n"
    return result

# Returns given week agenda #
def get_weekly(ldict, week_num):
    if week_num == 0:
        return "Error occured when processing data."
    week = "Wk" + str(week_num)
    day_order = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5}
    day_names = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat'}
    lst = []
    for mod in ldict:
        timeline = ldict[mod]["Timeline"]
        if week in timeline:
            for day in timeline[week]:
                for key, value in timeline[week][day].items():
                    lst.append([mod, day_order.get(day, 9), key, value])
    if lst == []:
        return "No classes in " + week + "."
    lst.sort(key=lambda lst: (lst[1], lst[2]))
    result = week + "\n"
    prev_day = -1
    for mod, day_num, key, value in lst:
        if day_num != prev_day:
            result += "\n" + day_names.get(day_num, "?") + ": \n"
            result += "    Date: " + value[2] + "\n"
            prev_day = day_num
        result += f"    {mod} => {key} | {value[0]} | {simplify_venue(value[1])}\n"
    return result

# Return week num and day of given date #
def check_what_week_day(timeline, test_date):
    for i, week in enumerate(timeline):
        for j, day in enumerate(week):
            if test_date == day:
                return i + 1, j
    return 0

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
    area_match = re.search(pattern, full)
    if not area_match:
        return abbrev
    area = area_match.group(0)
    if "LHN" in abbrev or "LHS" in abbrev:  # Means at the Arc
        tr = abbrev.split("-")[1]
        return tr + " " + area
    elif "LT" in abbrev or len(abbrev.split("-")) >= 3:  # Its a LT
        return abbrev + " " + area
    else:
        # Should be a TR
        return abbrev + " " + area

def combine_NTU_dict(ldict, timeline, file_name):
    final_dict = {}
    final_dict["file_name"] = file_name  # String
    final_dict["timeline"] = timeline  # List
    final_dict["mods"] = ldict  # Dict
    return final_dict

def test():
    test_data = create_timetable_list("STARS_NABIL.html")
    test_dict = compile_mods(test_data, "15/03/2025")
    print(test_dict)
