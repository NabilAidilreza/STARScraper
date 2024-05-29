from ntu_hub import create_timetable_list
from prettytable import *
import re
from ntu_extract_timetable import generate_timeline



from rich import print
from rich.table import Table
from rich.console import Console
from rich.theme import Theme

#! FILE THAT MANAGES LOCAL TABLE COMPARISON #

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
def compare_grp_timetables(file_name_array,wk_num,start_date,userich = False):
    #? Error Checkers #
    def check_file_name(file_name):
        if "_" not in file_name:
            return "Incorrect format. (No underscore in name)"
        elif ".html" not in file_name:
            return "Not a HTML file."
        else:
            try:
                testname = file_name.split("_")[2]
                return ""
            except:
                return "Incorrect format. (Follow recommended format)"
    def check_wk_num(wk_num):
        try:
            wk_num = int(wk_num)
            if wk_num > 13:
                return "Week number more than 13."
            if wk_num == 0:
                return "Zero value."
            return ""
        except:
            return "Not a number."
    def check_date(string):
        try:
            from datetime import datetime
            date = datetime.strptime(string, '%d/%M/%Y')
            return ""
        except ValueError:
            return "Use correct format. (DD/MM/YYYY)"
        
    #? Main function #
    #* Python Rich Init if Used #
    if userich:
        custom_theme = Theme({"success":"bold green","error":"bold red","alert":"bold orange_red1"})
        console = Console(theme=custom_theme,record=True)

    check_two = check_wk_num(wk_num)
    check_three = check_date(start_date)
    if check_two != "":
        console.print("Program exited.",style="error") if userich else print("Program exited.")
        console.print("Reason: " + check_two,style="alert") if userich else print("Reason: " + check_two)
        return
    if check_three != "":
        console.print("Program exited.",style="error") if userich else print("Program exited.")
        console.print("Reason: " + check_three,style="alert") if userich else print("Reason: " + check_three)
        return

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

    try:
        timeline = generate_timeline(start_date)
    except ValueError:
        console.print("[error]Error occurred:[/error]" + "[alert] Unknown date string![/alert]\n[error]Exiting program...[/error]") if userich else print("Error occurred: Unknown date string!\nExiting program...")
    
    DATES = {}
    for i in range(len(timeline)):
        if i == 0:
            continue
        else:
            DATES[i] = timeline[i-1][0] + " to " + timeline[i-1][-2]

    # For day indexing #
    dayref = ["Mon","Tue","Wed","Thu","Fri","Sat"]
    # For printing #
    DAYS = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"]
    PERIODS = ["0830to0920", "0930to1020", "1030to1120", "1130to1220", "1230to1320", "1330to1420", "1430to1520", "1530to1620", "1630to1720", "1730to1820","1830to1920","1930to2020","2030to2120","2130to2220"]
    lst = []

    # #! TEST CASE #
    # file_name_array[3] = "YIKES_html"
    # #! --------- #

    # Extract all tables #
    errorList = []
    for file in file_name_array:
        try:
            temp = create_timetable_list(file)
            temp.pop(0)
            lst.append(temp)
            console.print("File: " + file + " -> [success]success![/success]") if userich else print("File: " + file + " -> success!")
        except Exception:
            console.print("File: " + file + " -> [error]error![/error]") if userich else print("File: " + file + " -> error!")
            errorList.append(file)
    if len(errorList) != 0:
        for errorFile in errorList:
            file_name_array.remove(errorFile)
            console.print("File: " + errorFile + " removed from stack.",style="alert") if userich else print("File: " + errorFile + " removed from stack.")
            console.print("Reason: " + check_file_name(errorFile),style="alert") if userich else print("Reason: " + check_file_name(errorFile))

            
    # Set up day tables #
    MONDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    TUESDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    WEDNESDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    THURSDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    FRIDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    SATURDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    WEEK = [MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY,SATURDAY]
    
    #? Sorting data #
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
    
    #? Create chart #
    if userich:
        console.print(f"\n\nTeaching Week {str(wk_num)} -> {DATES[wk_num]}")
        def setupTable(day):
            table = Table(title=f"{day[0] + day[1:].lower()}")
            lst = []
            table.add_column("Period",style="orange_red1",justify="center")
            for name in file_name_array:
                col_name = name.split("_")[2]
                table.add_column(col_name,style="cyan",justify="center")
            return table
        for i in range(len(WEEK)):
            table = setupTable(DAYS[i])
            transposed_data = list(map(list, zip(*WEEK[i])))
            for i in range(len(transposed_data)):
                row = transposed_data[i]
                row.insert(0,PERIODS[i])
                table.add_row(*row)
            console.print(table)
        file_name = f"comparison_tables\WEEK_" + str(wk_num) + "_TABLE.txt"
        console.save_text(file_name)
        return file_name
    else:
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