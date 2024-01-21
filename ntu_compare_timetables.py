from ntu_hub import create_timetable_list
from prettytable import *
import re
from ntu_extract_timetable import generate_timeline

# Clean venue string via regex #
def check_venue(char):
    # Regular expression pattern to match text within parentheses
    pattern = r'\((.*?)\)'
    # Find the first occurrence of the pattern in the input string
    common_term = re.search(pattern, char)
    if common_term != None:
        # Get the matched text
        venue = common_term.group(0)
        if "The " in venue:
            # Remove "The " from the venue name
            venue = venue.replace("The ", "")
    else:
        # Regular expression pattern to match text before a hyphen
        pattern = r'^.*?-'
        # Find the first occurrence of the pattern in the input string
        common_term = re.search(pattern, char)
        if common_term != None:
            # Add parentheses around the matched text
            venue = "(" + common_term.group(0)[:-1] + ")"
        else:
            venue = '-'
        if "LHS" in char:
            venue = "(Hive)"
        else:
            if "LHN" in char:
                venue = "(Arc)"
    return venue

# Creates a txt file to compare schedules #
def compare_grp_timetables(file_name_array,wk_num,start_date):
    NUMBER_OF_PPL = len(file_name_array)
    teaching_wk = "Teaching Wk" + str(wk_num)
    time_periods = {"08":0,
                    "09":1,
                    "10":2,
                    "11":3,
                    "12":4,
                    "13":5,
                    "14":6,
                    "15":7,
                    "16":8,
                    "17":9,
                    "18":10,
                    "19":11,
                    "20":12,
                    "21":13,
                    "22":14}
    timeline = generate_timeline(start_date)
    DATES = {}
    for i in range(len(timeline)):
        if i == 0:
            continue
        else:
            DATES[i] = timeline[i-1][0] + " to " + timeline[i-1][-2]
    ###
    # For day indexing #
    dayref = ["Mon","Tue","Wed","Thu","Fri","Sat"]
    # For printing #
    DAYS = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"]
    PERIODS = ["0830to0920", "0930to1020", "1030to1120", "1130to1220", "1230to1320", "1330to1420", "1430to1520", "1530to1620", "1630to1720", "1730to1820","1830to1920","1930to2020","2030to2120","2130to2220"]
    lst = []
    # Extract all tables #
    for file in file_name_array:
        temp = create_timetable_list(file)
        temp.pop(0)
        lst.append(temp)
        print("File: " + file + " -> success!")
    # Set up day tables #
    MONDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    TUESDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    WEDNESDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    THURSDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    FRIDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    SATURDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    WEEK = [MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY,SATURDAY]
    #print("\nComparing tables...")
    for i in range(len(lst)):
        for week in lst[i]:
            for item in week:
                # Display formatting #
                result = item[0] + " " + (item[9][:3] if item[9] == "Lec/Stu" else item[9]) + " " + check_venue(item[13])
                week = item[14]
                if week == teaching_wk:
                    day = item[11]
                    day_index = dayref.index(day)
                    datetime = item[12]
                    if "-" in datetime:
                        datetime = datetime.replace("-","to")
                    startstamp = datetime[:2]
                    endstamp = datetime[6:8]
                    # Determine num of period slots per module #
                    period_num = time_periods[endstamp]-time_periods[startstamp]
                    if startstamp in time_periods:
                        start_index = time_periods[startstamp]
                        # Add mod to correct period #
                        if period_num >= 2:
                            for m in range(period_num):
                                WEEK[day_index][i][start_index] = result
                                start_index += 1
                        else:
                            WEEK[day_index][i][start_index] = result
    #print("Generating comparison chart...")
    # Print and create txt file #
    lst = []
    for name in file_name_array:
        name = name.split("_")[2]
        lst.append(name)
    def create_pretty_table():
        x = PrettyTable()
        x.field_names = lst
        return x
    file_name = "comparison_tables\WEEK_" + str(wk_num) + "_TABLE.txt"
    f = open(file_name,"w")
    f.write("*-----------------------------------------------------------*\n")
    f.write("            TEACHING WEEK " + str(wk_num) + " -> " + DATES[wk_num] + "\n")
    f.write("*-----------------------------------------------------------*\n\n")
    for i in range(len(WEEK)):
        x = create_pretty_table()
        transposed_data = list(map(list, zip(*WEEK[i])))
        x.add_rows(transposed_data)
        fieldname = 'Period'
        x._field_names.insert(0, fieldname) 
        x._align[fieldname] = 'c' 
        x._valign[fieldname] = 't' 
        for n, _ in enumerate(x._rows): 
            x._rows[n].insert(0, PERIODS[n]) 
        f.write(DAYS[i]+"\n")
        f.write(x.get_string() + '\n\n')
    f.close()
    print("\n\n !!! SUCCESS !!! \n\n")
    print("Txt file created... -> WEEK_" + str(wk_num) + "_TABLE.txt\n")
    return file_name

### REFERENCES ###
# Course No 1
# Title 2
# AU 3
# CourseType 4
# S/U Grade option 5
# GERType 6
# IndexNumber 7
# Status 8
# Choice 9
# ClassType 10
# Group 11
# Day 12
# Time 13
# Venue 14
# Remark 15
# Exam 16