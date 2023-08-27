from extract_timetable import create_timetable_list
from prettytable import *

def compare_grp_timetables(file_name_array,wk_num):
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
                    "18":10}
    DATES = {1:'14/8/23 to 18/8/23',
            2:'21/8/23 to 25/8/23',
            3:'28/8/23 to 1/9/2023',
            4:'4/9/23 to 8/9/2023',
            5:'11/9/23 to 15/9/23',
            6:'18/9/23 to 22/9/23',
            7:'25/9/23 to 29/9/23',
            0:'2/10/23 to 6/10/2023', # RECESS WEEK
            8:'9/10/23 to 13/10/23',
            9:'16/10/23 to 20/10/23',
            10:'23/10/23 to 27/10/23',
            11:'30/10/23 to 3/11/2023',
            12:'6/11/23 to 10/11/2023',
            13:'13/11/23 to 17/11/2023'}
    DAYS = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY"]
    PERIODS = ["0830to0920", "0930to1020", "1030to1120", "1130to1220", "1230to1320", "1330to1420", "1430to1520", "1530to1620", "1630to1720", "1730to1820","1830to1920"]
    lst = []
    # Extract all tables #
    for file in file_name_array:
        #print("File: " + file)
        temp = create_timetable_list(file)
        temp.pop(0)
        lst.append(temp)
        #print("Moving to next file...")
    # Set up day tables #
    MONDAY = [["" for _ in range(11)] for _ in range(NUMBER_OF_PPL)]
    TUESDAY = [["" for _ in range(11)] for _ in range(NUMBER_OF_PPL)]
    WEDNESDAY = [["" for _ in range(11)] for _ in range(NUMBER_OF_PPL)]
    THURSDAY = [["" for _ in range(11)] for _ in range(NUMBER_OF_PPL)]
    FRIDAY = [["" for _ in range(11)] for _ in range(NUMBER_OF_PPL)]
    WEEK = [MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY]

    for i in range(len(lst)):
        for week in lst[i]:
            for item in week:
                #if item[14] == "Teaching Wk1":
                if item[14] == teaching_wk:
                    if item[11] == "Mon":
                        startstamp = item[12][:2]
                        endstamp = item[12][6:8]
                        #print(item[12],item[0])
                        # Determine num of period slots per module #
                        period_num = time_periods[endstamp]-time_periods[startstamp]
                        if startstamp in time_periods:
                            start_index = time_periods[startstamp]
                            # Add mod to correct period #
                            if period_num >= 2:
                                for m in range(period_num):
                                    WEEK[0][i][start_index] = item[0] + " " + item[9]
                                    start_index += 1
                            else:
                                WEEK[0][i][start_index] = item[0] + " " + item[9]
                    if item[11] == "Tue":
                        startstamp = item[12][:2]
                        endstamp = item[12][6:8]
                        period_num = time_periods[endstamp]-time_periods[startstamp]
                        if startstamp in time_periods:
                            start_index = time_periods[startstamp]
                            if period_num >= 2:
                                for m in range(period_num):
                                    WEEK[1][i][start_index] = item[0] + " " + item[9]
                                    start_index += 1
                            else:
                                WEEK[1][i][start_index] = item[0] + " " + item[9]
                    if item[11] == "Wed":
                        startstamp = item[12][:2]
                        endstamp = item[12][6:8]
                        period_num = time_periods[endstamp]-time_periods[startstamp]
                        if startstamp in time_periods:
                            start_index = time_periods[startstamp]
                            if period_num >= 2:
                                for m in range(period_num):
                                    WEEK[2][i][start_index] = item[0] + " " + item[9]
                                    start_index += 1
                            else:
                                WEEK[2][i][start_index] = item[0] + " " + item[9]
                    if item[11] == "Thu":
                        startstamp = item[12][:2]
                        endstamp = item[12][6:8]
                        period_num = time_periods[endstamp]-time_periods[startstamp]
                        if startstamp in time_periods:
                            start_index = time_periods[startstamp]
                            if period_num >= 2:
                                for m in range(period_num):
                                    WEEK[3][i][start_index] = item[0] + " " + item[9]
                                    start_index += 1
                            else:
                                WEEK[3][i][start_index] = item[0] + " " + item[9]
                    if item[11] == "Fri":
                        startstamp = item[12][:2]
                        endstamp = item[12][6:8]
                        period_num = time_periods[endstamp]-time_periods[startstamp]
                        if startstamp in time_periods:
                            start_index = time_periods[startstamp]
                            if period_num >= 2:
                                for m in range(period_num):
                                    WEEK[4][i][start_index] = item[0] + " " + item[9]
                                    start_index += 1
                            else:
                                WEEK[4][i][start_index] = item[0] + " " + item[9]
    def create_pretty_table():
        x = PrettyTable()
        x.field_names = file_name_array
        return x

    print("*-----------------------------------------------------------*")
    print("            TEACHING WEEK " + str(wk_num) + " -> " + DATES[wk_num])
    print("*-----------------------------------------------------------*\n")
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
        print(DAYS[i])
        print(x)
        print("\n")
        
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