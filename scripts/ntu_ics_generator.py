import os
import uuid
from datetime import datetime, timedelta

import x_wr_timezone
from icalendar import Calendar, Event
from rich.console import Console
from rich.theme import Theme

from .ntu_check_exam_schedules import split_date_time
from .ntu_extract_timetable import (
    AU,
    CLASS_TYPE,
    COURSE_CODE,
    COURSE_TITLE,
    DAY,
    DAY_ORDER,
    EXAM,
    GROUP,
    INDEX_NUMBER,
    STATUS,
    TIME,
    VENUE,
    create_timetable_list,
    read_html_file,
    teaching_week_start,
)

# FILE THAT MANAGES ICS FILE CREATION #

# Generates an ics file #
def generate_ics_file(FILE_NAME, START_DATE):
    #? Error Checkers #
    def check_file_name(file_name):
        if "_" not in file_name:
            return "Incorrect format. (No underscore in name)"
        elif ".html" not in file_name:
            return "Not a HTML file."
        else:
            try:
                read_html_file(file_name)
                return ""
            except FileNotFoundError:
                return "File not found."

    def check_date(string):
        try:
            datetime.strptime(string, '%d/%m/%Y')
            return ""
        except ValueError:
            return "Use correct format. (DD/MM/YYYY)"

    #? Main function #
    #* Python Rich Init #
    custom_theme = Theme({"success": "bold green", "error": "bold red", "warning": "bold orange_red1", "process": "blue_violet"})
    console = Console(theme=custom_theme, record=True)

    name_check = check_file_name(FILE_NAME)
    if name_check != "":
        console.print("Program exited..", style="error")
        console.print("Reason: " + name_check, style="warning")
        return
    date_check = check_date(START_DATE)
    if date_check != "":
        console.print("Program exited.", style="error")
        console.print("Reason: " + date_check, style="warning")
        return

    # Requires file name (STAR Planner Html) & first day of first teaching week of semester #
    try:
        modules_list = create_timetable_list(FILE_NAME)
    except (ValueError, IndexError) as e:
        console.print("[error]Error occurred.[/error]")
        console.print("[warning]" + str(e) + "[/warning]")
        console.print("[error]Program exited.[/error]")
        return

    console.print("Preparing calender file...", style="process")
    # Create a new calendar #
    cal = Calendar()
    # Set calendar metadata #
    cal.add('prodid', '-//sebbo.net//ical-generator//EN')
    cal.add('version', '2.0')
    cal.add('NAME', 'NTU Course Timetable')
    cal.add('X-WR-CALNAME', 'NTU Course Timetable')
    console.print("Extracting modules...", style="bold blue")
    for i in range(1, len(modules_list)):
        for m in range(len(modules_list[i])):
            mod = modules_list[i][m]
            # Check status for rare cases (waitlist, exempted, etc) * #
            if mod[STATUS] != "Registered":
                continue
            # Get date via week and day indexing (recess week is accounted for) #
            day = mod[DAY]
            if day not in DAY_ORDER:
                continue
            j = DAY_ORDER.index(day)
            date = teaching_week_start(i, START_DATE) + timedelta(days=j)
            # Prep data for each mod #
            time = mod[TIME]
            if "-" in time:
                time = time.replace("-", "to")
            summary = mod[COURSE_CODE] + " " + mod[COURSE_TITLE]
            location = mod[VENUE]
            description = "Class Type: " + mod[CLASS_TYPE] + "\n" + "Index: " + mod[INDEX_NUMBER] + "\n" + "Group: " + mod[GROUP] + "\n" + "Remarks: " + f'Week {i}' + "\n" + "Exam: " + mod[EXAM] + "\n" + "AUs: " + mod[AU]
            try:
                start_hh, start_mm = time.split("to")[0][:2], time.split("to")[0][2:4]
                end_hh, end_mm = time.split("to")[1][:2], time.split("to")[1][2:4]
                dtstart = date + timedelta(hours=int(start_hh), minutes=int(start_mm))
                dtend = date + timedelta(hours=int(end_hh), minutes=int(end_mm))
            except (ValueError, IndexError):
                continue
            category = mod[COURSE_CODE]
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
    console.print("Writing calendar to .ics file...", style="bold yellow")
    # Save the calendar to an .ics file #
    with open('in.ics', 'wb') as f:
        f.write(cal.to_ical())
    with open("in.ics", 'rb') as file:
        calendar = Calendar.from_ical(file.read())
        new_calendar = x_wr_timezone.to_standard(calendar)
    name_part = os.path.basename(FILE_NAME).split(".")[0].split("_")[-1]
    FINAL_FILE_NAME = name_part + '_calendar.ics'
    with open(FINAL_FILE_NAME, 'wb') as file:
        file.write(new_calendar.to_ical())
    # Ensure the output folder exists #
    output_dir = os.path.join(os.getcwd(), "calendars")
    os.makedirs(output_dir, exist_ok=True)
    final_path = os.path.join(output_dir, FINAL_FILE_NAME)
    os.replace(os.path.join(os.getcwd(), FINAL_FILE_NAME), final_path)
    # Clean up temp file #
    if os.path.exists('in.ics'):
        os.remove('in.ics')
    console.print(f"[success]Calender file has been created.[/success] \n[warning]File is saved here:[/warning] {final_path}", style="bold yellow")
    return FINAL_FILE_NAME


# Generates an exam-only .ics file (exam dates & timings) from a STAR Planner HTML file #
def generate_exam_ics_file(FILE_NAME):
    #? Error Checkers #
    def check_file_name(file_name):
        if "_" not in file_name:
            return "Incorrect format. (No underscore in name)"
        elif ".html" not in file_name:
            return "Not a HTML file."
        else:
            try:
                read_html_file(file_name)
                return ""
            except FileNotFoundError:
                return "File not found."

    #? Main function #
    #* Python Rich Init #
    custom_theme = Theme({"success": "bold green", "error": "bold red", "warning": "bold orange_red1", "process": "blue_violet"})
    console = Console(theme=custom_theme, record=True)

    name_check = check_file_name(FILE_NAME)
    if name_check != "":
        console.print("Program exited..", style="error")
        console.print("Reason: " + name_check, style="warning")
        return

    try:
        modules_list = create_timetable_list(FILE_NAME)
    except (ValueError, IndexError) as e:
        console.print("[error]Error occurred.[/error]")
        console.print("[warning]" + str(e) + "[/warning]")
        console.print("[error]Program exited.[/error]")
        return

    console.print("Preparing exam calendar file...", style="process")
    # Create a new calendar #
    cal = Calendar()
    # Set calendar metadata #
    cal.add('prodid', '-//sebbo.net//ical-generator//EN')
    cal.add('version', '2.0')
    cal.add('NAME', 'NTU Exam Schedule')
    cal.add('X-WR-CALNAME', 'NTU Exam Schedule')
    console.print("Extracting exams...", style="bold blue")
    seen_exams = set()
    exam_count = 0
    for i in range(1, len(modules_list)):
        for m in range(len(modules_list[i])):
            mod = modules_list[i][m]
            # Check status for rare cases (waitlist, exempted, etc) * #
            if mod[STATUS] != "Registered":
                continue
            # Skip modules without a valid exam date/time #
            exam_text = mod[EXAM].strip()
            if exam_text == "" or exam_text == "Not Applicable":
                continue
            date_part, time_part = split_date_time(exam_text)
            if not date_part or not time_part:
                continue
            # Deduplicate exams that appear on multiple teaching-week rows #
            exam_key = (mod[COURSE_CODE], date_part, time_part)
            if exam_key in seen_exams:
                continue
            seen_exams.add(exam_key)
            try:
                exam_date = datetime.strptime(date_part, "%d-%b-%Y")
                time = time_part.replace("-", "to")
                start_hh, start_mm = time.split("to")[0][:2], time.split("to")[0][2:4]
                end_hh, end_mm = time.split("to")[1][:2], time.split("to")[1][2:4]
                dtstart = exam_date + timedelta(hours=int(start_hh), minutes=int(start_mm))
                dtend = exam_date + timedelta(hours=int(end_hh), minutes=int(end_mm))
            except (ValueError, IndexError):
                continue
            # Prep data for each exam #
            summary = mod[COURSE_CODE] + " " + mod[COURSE_TITLE]
            description = "Exam: " + exam_text + "\n" + "Index: " + mod[INDEX_NUMBER] + "\n" + "AUs: " + mod[AU]
            category = mod[COURSE_CODE]
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
            event.add('description', description)
            event.add('dtstart', dtstart)
            event.add('dtend', dtend)
            event.add('categories', [category])
            cal.add_component(event)
            exam_count += 1

    if exam_count == 0:
        console.print("[warning]No exams found in the provided timetable.[/warning]")
        return

    console.print("Writing calendar to .ics file...", style="bold yellow")
    # Save the calendar to an .ics file #
    with open('in.ics', 'wb') as f:
        f.write(cal.to_ical())
    with open("in.ics", 'rb') as file:
        calendar = Calendar.from_ical(file.read())
        new_calendar = x_wr_timezone.to_standard(calendar)
    name_part = os.path.basename(FILE_NAME).split(".")[0].split("_")[-1]
    FINAL_FILE_NAME = name_part + '_exams.ics'
    with open(FINAL_FILE_NAME, 'wb') as file:
        file.write(new_calendar.to_ical())
    # Ensure the output folder exists #
    output_dir = os.path.join(os.getcwd(), "calendars")
    os.makedirs(output_dir, exist_ok=True)
    final_path = os.path.join(output_dir, FINAL_FILE_NAME)
    os.replace(os.path.join(os.getcwd(), FINAL_FILE_NAME), final_path)
    # Clean up temp file #
    if os.path.exists('in.ics'):
        os.remove('in.ics')
    console.print(f"[success]Exam calendar file has been created.[/success] \n[warning]File is saved here:[/warning] {final_path}", style="bold yellow")
    return FINAL_FILE_NAME
