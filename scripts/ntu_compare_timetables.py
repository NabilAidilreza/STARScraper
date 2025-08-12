import os
import re
from datetime import datetime
from .ntu_extract_timetable import generate_timeline, create_timetable_list
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from time import sleep

#! FILE THAT MANAGES LOCAL TABLE COMPARISON #

#? Helper functions #
def check_venue(venue_str):
    def normalize(v):
        v = v.strip().upper()
        if "CSKL" in v: return "CSKL"
        if "LHS" in v: return "Hive"
        if "LHN" in v: return "Arc"
        if "LAB" in v: return "Lab"
        if v.startswith("S"): return v[:2]
        return v

    # Early return if no brackets
    if "[" not in venue_str or "]" not in venue_str:
        return f"({venue_str})"

    # Case 1: code like CSKL12 at the start
    m = re.match(r'^([A-Za-z]{3,8})\d+', venue_str.strip())
    if m:
        return f"({normalize(m.group(1))})"

    # Case 2: check inside square brackets for known names
    m = re.search(r'\[([^\]]+)\]', venue_str)
    if m:
        inside = m.group(1)
        if "COMP LAB" in inside.upper() or "COMPUTER LAB" in inside.upper():
            return "(COMP)"

    # Case 3: extract before dash
    match = re.search(r'^.*?-', venue_str)
    if match:
        return f"({normalize(match.group(0)[:-1])})"

    # Case 4: extract from parentheses
    match = re.search(r'\((.*?)\)', venue_str)
    if match:
        v = match.group(1).replace("The ", "")
        return f"({normalize(v)})"

    return "(?)"

def get_name(file_name):
    return file_name.replace(".html","").split("_")[-1]

#? Error Checkers #
def check_file(file_name):
    if "_" not in file_name:
        return "Incorrect format. (No underscore in name)"
    if ".html" not in file_name:
        return "Not a HTML file."
    try:
        with open(file_name):
            pass
        return "Something went wrong... [Check breakpoint]"
    except FileNotFoundError:
        return "File not found."
    
def validate_week_number(wk_num):
    try:
        wk_num = int(wk_num)
        if wk_num > 13:
            return "Week number more than 13."
        if wk_num == 0:
            return "Zero value."
        return ""
    except ValueError:
        return "Not a number."
    
def validate_date(string):
    try:
        datetime.strptime(string, '%d/%M/%Y')
        return ""
    except ValueError:
        return "Use correct format. (DD/MM/YYYY)"
     
# Creates a txt file to compare schedules #
def compare_grp_timetables(file_names,wk_num,start_date):
    #? Console setup #
    custom_theme = Theme({"success":"bold green","error":"bold red","warning":"bold orange_red1","process":"blue_violet"})
    console = Console(theme=custom_theme,record=False)

    #? Check input params #
    week_num_error = validate_week_number(wk_num)
    date_error = validate_date(start_date)
    if week_num_error != "":
        console.print("Program exited.",style="error")
        console.print("Reason: " + week_num_error,style="warning")
        return
    if date_error != "":
        console.print("Program exited.",style="error")
        console.print("Reason: " + date_error,style="warning")
        return

    try:
        console.print("Creating timeline...",style="process")
        timeline = generate_timeline(start_date)
    except ValueError:
        console.print("[error]Error occurred:[/error]" + "[warning] Unknown date string![/warning]\n[error]Exiting program...[/error]")
        return

    NUMBER_OF_PPL = len(file_names)

    #? For week indexing #
    teaching_wk = "Teaching Wk" + str(wk_num)
    DATES = {i: f"{timeline[i-1][0]} to {timeline[i-1][-2]}" for i in range(1, len(timeline))}
    #? For day indexing #
    dayref = ["Mon","Tue","Wed","Thu","Fri","Sat"]
    DAYS = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"]
    # For period index
    time_periods = {str(i).zfill(2): idx for idx, i in enumerate(range(8, 23))}
    #? For period printing #
    PERIODS = [f"{i:02}30to{(i+1):02}20" for i in range(8, 22)]
    timetables = []
    errorList = []
    console.print("Reading files...",style="process")

    for file in file_names:
        try:
            timetable = create_timetable_list(file)[1:]
            timetables.append(timetable)
            console.print("File: " + file + " -> [success]success![/success]")
        except Exception:
            console.print("File: " + file + " -> [error]error![/error]")
            errorList.append(file)
    
    for errorFile in errorList:
        file_names.remove(errorFile)
        console.print("File: " + errorFile + " removed from stack.",style="warning")
        console.print("Reason: " + check_file(errorFile),style="warning")
        
    # Set up day tables #
    MONDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    TUESDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    WEDNESDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    THURSDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    FRIDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    SATURDAY = [["" for _ in range(14)] for _ in range(NUMBER_OF_PPL)]
    WEEK = [MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY,SATURDAY]

    console.print("Sorting events...",style="process")

    #? Sorting data #
    for i in range(len(timetables)):
        #? lst[i] => person items
        for week in timetables[i]:
            for item in week:
                status = item[7]
                if status == "Waitlist" or status == "*Exempted" or status != "Registered":
                    continue
                # Display formatting #
                result = item[0] + " " + (item[9][:3] if item[9] == "Lec/Stu" else item[9]) + " " + check_venue(item[13])
                week = item[14]
                # For indicating "50" timings
                is_fifty = False
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
                        if datetime[8:] == "50":
                            period_num += 1 # For display purposes
                            is_fifty = True
                        if period_num >= 2:
                            if is_fifty:
                                for m in range(period_num-1):
                                    WEEK[day_index][i][start_index] = result
                                    start_index += 1
                                WEEK[day_index][i][start_index] = result + " *"
                                start_index += 1
                            else:
                                for m in range(period_num):
                                    WEEK[day_index][i][start_index] = result
                                    start_index += 1
                        else:
                            WEEK[day_index][i][start_index] = result

    console.print("Creating chart...",style="process")
    console = Console(theme=custom_theme,record=True)
    console.print(f"\n\nTeaching Week {str(wk_num)} -> {DATES[wk_num]}")
    #? Lunch Logic #
    FREE = [{DAYS[_]:{}} for _ in range(len(DAYS))]

    def create_day_table(day):
        table = Table(title=f"{day.capitalize()}",show_lines=False)
        table.add_column("Period",style="orange_red1",justify="center")
        for name in file_names:
            table.add_column(get_name(name),style="cyan",justify="center")
        return table
    
    for i in range(len(WEEK)):
        table = create_day_table(DAYS[i])
        transposed_data = list(map(list, zip(*WEEK[i])))
        for m in range(len(transposed_data)):
            row = transposed_data[m]
            if len(errorList) != 0:
                row = row[:-len(errorList)]
            FREE[i][DAYS[i]][PERIODS[m] if m in [3,4,5] else ""] = [get_name(file_names[j]) for j in range(len(row)) if row[j] == ""]
            row.insert(0,PERIODS[m])
            table.add_row(*row)
        if DAYS[i] != "SATURDAY":
            console.print(table)
            sleep(0.5)

    #? Lunch Table Creation #
    evenodd = "Even Wk" if wk_num % 2 == 0 else "Odd Wk"
    lunch_table_title = f"Possible Weekly Lunch Timings ({evenodd})"
    lunch_table = Table(title=lunch_table_title)
    lunch_table.add_column("Day",style="green",justify="center")
    lunch_table.add_column("Period",style="orange_red1",justify="center")
    lunch_table.add_column("Names",style="cyan")
    lunch_table.add_column("Pax",style="yellow")

    free_timings = []
    for j in range(len(FREE)):
        day = FREE[j][DAYS[j]]
        day_temp = [["",period,",".join(day[period]),str(len(day[period]))] for period in day.keys()]
        day_temp.pop(0) if day_temp[0][1] == "" else day_temp
        day_temp[0][0] = dayref[j]
        free_timings.append(day_temp)
    for row in free_timings:
        for col in row:
            lunch_table.add_row(*col)
    console.print(lunch_table)

    if not os.path.exists("comparison_tables"):
        os.makedirs("comparison_tables")
    file_name = f"comparison_tables\\WEEK_" + str(wk_num) + "_TABLE.html"
    console.save_html(file_name)
    final_dir = os.path.abspath(file_name)
    console.print(f"[success]Txt file has been created for reference.[/success] \n[warning]File is saved here:[/warning] {final_dir}",style="bold yellow")
    return file_name
