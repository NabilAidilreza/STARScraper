import os
import uuid
from icalendar import Calendar, Event
import x_wr_timezone
from datetime import datetime,timedelta
from extract_timetable import create_timetable_list # Get extracted timetable from NTU STARS Planner


def generate_ics_file(FILE_NAME,START_DATE):
    # Requires file name (STAR Planner Html) & first day of first teaching week of semester
    modules_list = create_timetable_list(FILE_NAME)
    SD = START_DATE.split("/")
    startday = datetime(int(SD[-1]), int(SD[1][1]) if SD[1][0] == "0" else int(SD[1]), int(SD[0]), 0, 0, 0)   

    print("Preparing calendar...")
    # Create a new calendar
    cal = Calendar()
    # Set calendar metadata
    cal.add('prodid', '-//sebbo.net//ical-generator//EN')
    cal.add('version', '2.0')
    cal.add('NAME', 'NTU Course Timetable')
    cal.add('X-WR-CALNAME', 'NTU Course Timetable')

    print("Adding courses...")
    for i in range(len(modules_list)):
        if i == 0:
            continue
        for m in range(len(modules_list[i])):
            j = 0
            if modules_list[i][m][11] == "Mon":
                j = 0
            elif modules_list[i][m][11] == "Tue":
                j = 1
            elif modules_list[i][m][11] == "Wed":
                j = 2
            elif modules_list[i][m][11] == "Thu":
                j = 3
            elif modules_list[i][m][11] == "Fri":
                j = 4        

            if modules_list[i][m][7] == "Waitlist" or modules_list[i][m][7] == "*Exempted":
                continue
            #day = modules_list[i][m][11]

            if i >= 8:
                date = startday + timedelta(days=(7*(i))+j)
            else:
                date = startday + timedelta(days=(7*(i-1))+j)

            time = modules_list[i][m][12]

            #mod_name = modules_list[i][m][0]

            #week = modules_list[i][m][-2]
            #print(f'{mod_name} - - - {day} - - - {time} - - - {date} - - - {week}')

            summary = modules_list[i][m][0] + " " + modules_list[i][m][1]
            location = modules_list[i][m][13]
            description = "Class Type: " + modules_list[i][m][9] + "\n" + "Index: " + modules_list[i][m][6] + "\n" + "Group: " + modules_list[i][m][10] + "\n" + "Remarks: " + f'Week {i}' + "\n" + "Exam: " + modules_list[i][m][15] + "\n" + "AUs: " + modules_list[i][m][2]
            dtstart = date + timedelta(hours=int(time.split("to")[0][:2]), minutes=int(time.split("to")[0][2:]))
            dtend = date + timedelta(hours=int(time.split("to")[1][:2]), minutes=int(time.split("to")[1][2:]))
            category = modules_list[i][m][0]

            # Create an event #
            event = Event()
            # Assign timestampe and UID #
            timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
            random_id = str(uuid.uuid4())
            uid = f'{timestamp}-{random_id}'
            event.add('uid', uid)
            event.add('dtstamp', datetime.now())
            event.add('summary', summary)
            event.add('location', location)
            event.add('description', description)
            event.add('dtstart', dtstart)
            event.add('dtend', dtend)
            event.add('categories', [category])
            cal.add_component(event)

    print("Writing calendar to .ics file...")

    # Save the calendar to an .ics file
    with open('in.ics', 'wb') as f:
        f.write(cal.to_ical())
    with open("in.ics", 'rb') as file:
        calendar = Calendar.from_ical(file.read())
        new_calendar = x_wr_timezone.to_standard(calendar)
    # you could use the new_calendar variable now
    FILE_NAME = FILE_NAME.split(".")[0].split("_")[-1]
    with open(FILE_NAME + '_calendar.ics', 'wb') as file:
        file.write(new_calendar.to_ical())
    os.remove('in.ics')

    # Get the absolute path of the saved file
    absolute_path = os.path.abspath('calendar.ics')
    print("Calender file has been created. \n File is saved here: " + absolute_path + " :::")

    ### TEST CODES ###
    #for week in modules_list:
    #    for module in week:
    #        print(module)

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
    # Remark 15
    # Exam 16

    # Summary -> Course Code + Course Name
    # Location -> Location
    # Description -> Class Type, Group, Remarks, Exam, AUs
    # DTSTART -> Date + StartTime
    # DTEND -> Date + EndTime
    # Category -> Course Code


