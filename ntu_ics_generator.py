import os
import uuid
from icalendar import Calendar, Event
import x_wr_timezone
from datetime import datetime,timedelta
from ntu_hub import create_timetable_list

from rich import print
from rich.table import Table
from rich.console import Console
from rich.theme import Theme

#! FILE THAT MANAGES ICS FILE CREATION #

# Generates an ics file #
def generate_ics_file(FILE_NAME,START_DATE):
    #? Error Checkers #
    def check_file_name(file_name):
        if "_" not in file_name:
            return "Incorrect format. (No underscore in name)"
        elif ".html" not in file_name:
            return "Not a HTML file."
        else:
            try:
                file = open(file_name)
                file.close()
                return ""
            except:
                return "File not found."
    def check_date(string):
        try:
            from datetime import datetime
            date = datetime.strptime(string, '%d/%M/%Y')
            return ""
        except ValueError:
            return "Use correct format. (DD/MM/YYYY)"
        
    #? Main function #
    #* Python Rich Init #
    custom_theme = Theme({"success":"bold green","error":"bold red","warning":"bold orange_red1","process":"blue_violet"})
    console = Console(theme=custom_theme,record=True)

    name_check = check_file_name(FILE_NAME)
    if name_check != "":
        console.print("Program exited..",style="error")
        console.print("Reason: " + name_check,style="warning")
        return
    date_check = check_date(START_DATE)
    if date_check != "":
        console.print("Program exited.",style="error")
        console.print("Reason: " + date_check,style="warning")
        return
    
    # Requires file name (STAR Planner Html) & first day of first teaching week of semester #
    try:
        modules_list = create_timetable_list(FILE_NAME)
    except ValueError:
        console.print("[error]Error occurred.[/error]\n[error]Program exited.[/error]")
    
    SD = START_DATE.split("/")
    startday = datetime(int(SD[-1]), int(SD[1][1]) if SD[1][0] == "0" else int(SD[1]), int(SD[0]), 0, 0, 0)   
    console.print("Preparing calender file...",style="process")
    # Create a new calendar #
    cal = Calendar()
    # Set calendar metadata #
    cal.add('prodid', '-//sebbo.net//ical-generator//EN')
    cal.add('version', '2.0')
    cal.add('NAME', 'NTU Course Timetable')
    cal.add('X-WR-CALNAME', 'NTU Course Timetable')
    console.print("Extracting modules...",style="bold blue")
    dayref = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    for i in range(len(modules_list)):
        # Fix Indexing (Wk1-13) #
        if i == 0:
            continue
        for m in range(len(modules_list[i])):
            # Set indexing for days #
            day = modules_list[i][m][11]
            j = dayref.index(day)
            # Check status for rare cases (waitlist, exempted, etc) * #
            status = modules_list[i][m][7]
            if status == "Waitlist" or status == "*Exempted" or status != "Registered":
                continue
            # Get date via week and day indexing # 
            if i >= 8:
                date = startday + timedelta(days=(7*(i))+j)
            else:
                date = startday + timedelta(days=(7*(i-1))+j)
            # Prep data for each mod #
            time = modules_list[i][m][12]
            if "-" in time:
                time = time.replace("-","to")
            summary = modules_list[i][m][0] + " " + modules_list[i][m][1]
            location = modules_list[i][m][13]
            description = "Class Type: " + modules_list[i][m][9] + "\n" + "Index: " + modules_list[i][m][6] + "\n" + "Group: " + modules_list[i][m][10] + "\n" + "Remarks: " + f'Week {i}' + "\n" + "Exam: " + modules_list[i][m][15] + "\n" + "AUs: " + modules_list[i][m][2]
            dtstart = date + timedelta(hours=int(time.split("to")[0][:2]), minutes=int(time.split("to")[0][2:]))
            dtend = date + timedelta(hours=int(time.split("to")[1][:2]), minutes=int(time.split("to")[1][2:]))
            category = modules_list[i][m][0]
            # Create an event #
            event = Event()
            # Assign timestamps and UID #
            timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
            random_id = str(uuid.uuid4())
            uid = f'{timestamp}-{random_id}'
            # Provide details to event object #
            event.add('uid', uid)
            event.add('dtstamp', datetime.now())
            event.add('summary', summary)
            event.add('location', location)
            event.add('description', description)
            event.add('dtstart', dtstart)
            event.add('dtend', dtend)
            event.add('categories', [category])
            cal.add_component(event)
    console.print("Writing calendar to .ics file...",style="bold yellow")
    #print("Writing calendar to .ics file...")
    # Save the calendar to an .ics file
    with open('in.ics', 'wb') as f:
        f.write(cal.to_ical())
    with open("in.ics", 'rb') as file:
        calendar = Calendar.from_ical(file.read())
        new_calendar = x_wr_timezone.to_standard(calendar)
    FILE_NAME = FILE_NAME.split(".")[0].split("_")[-1]
    FINAL_FILE_NAME = FILE_NAME + '_calendar.ics'
    with open(FINAL_FILE_NAME, 'wb') as file:
        file.write(new_calendar.to_ical())
    os.remove('in.ics')
    # Get the absolute path of the saved file
    main_dir = os.path.dirname(os.path.abspath(FINAL_FILE_NAME))
    final_dir = main_dir+"\\calendars\\"+FINAL_FILE_NAME
    os.replace(main_dir+"/"+FINAL_FILE_NAME, final_dir)
    console.print(f"[success]Calender file has been created.[/success] \n[warning]File is saved here:[/warning] {final_dir}",style="bold yellow")

    ### REFERENCE CODE ###
    # Create an event #
    #event = Event()
    # Assign timestampe and UID #
    #timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    #random_id = str(uuid.uuid4())
    #uid = f'{timestamp}-{random_id}'
    #event.add('uid', uid)
    #event.add('dtstamp', datetime.now())
    #event.add('summary', 'Event 1')
    #event.add('location', 'Event 1')
    #event.add('description', 'Event 1')
    #event.add('dtstart', datetime(2023, 8, 15, 10, 0, 0))
    #event.add('dtend', datetime(2023, 8, 15, 12, 0, 0))
    #event.add('categories', ['Work'])
    #cal.add_component(event)

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
    # Wk 15
    # Exam 16

    # Summary -> Course Code + Course Name
    # Location -> Location
    # Description -> Class Type, Group, Remarks, Exam, AUs
    # DTSTART -> Date + StartTime
    # DTEND -> Date + EndTime
    # Category -> Course Code


