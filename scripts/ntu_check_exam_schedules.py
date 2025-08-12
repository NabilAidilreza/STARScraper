from .ntu_extract_timetable import create_timetable_list
from .ntu_compare_timetables import validate_date,check_file,get_name
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from collections import defaultdict

def split_date_time(exam_str):
    # Example: "04-Dec-2025 0900to1100 hrs "
    exam_str = exam_str.strip().replace(" hrs", "")
    date_part, time_part = exam_str.split(" ", 1)
    return date_part, time_part

def check_exam_schedules(file_names,start_date):
    #? Console setup #
    custom_theme = Theme({"success":"bold green","error":"bold red","warning":"bold orange_red1","process":"blue_violet"})
    console = Console(theme=custom_theme,record=False)

    #? Check input params #
    date_error = validate_date(start_date)
    if date_error != "":
        console.print("Program exited.",style="error")
        console.print("Reason: " + date_error,style="warning")
        return

    NUMBER_OF_PPL = len(file_names)

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

    console.print("Sorting events...",style="process")

    exam_dates = []
    #? Sorting data #
    for i in range(len(timetables)):
        unique_exams = []       # List to hold unique exams for this person
        seen_exams = set()      # Set to quickly check for duplicates

        for week in timetables[i]:
            for item in week:
                status = item[7]
                # Skip exams if status is Waitlist, Exempted, or not Registered
                if status == "Waitlist" or status == "*Exempted" or status != "Registered":
                    continue
                
                # Only consider exams with a valid exam date/time (not "Not Applicable")
                if item[15] != "Not Applicable":
                    date, timing = split_date_time(item[15])  # Split exam date/time
                    exam_info = (item[0], date, timing)       # Tuple: (course, date, timing)
                    
                    # Add only if exam_info is not already recorded for this person
                    if exam_info not in seen_exams:
                        seen_exams.add(exam_info)
                        unique_exams.append(list(exam_info))
                else:
                    continue

        exam_dates.append(unique_exams)   # Add this person's unique exams to master list

    # Build a schedule dictionary keyed by (date, time) holding a list of (person, course) tuples
    exam_schedule = defaultdict(list)

    # Extract person names from filenames (assumed function get_name exists)
    names = [get_name(filename) for filename in file_names]

    # Populate exam_schedule with person and their courses for each exam slot
    for person_idx, exams in enumerate(exam_dates):
        person = names[person_idx]
        for course, date, time in exams:
            exam_schedule[(date, time)].append((person, course))

    # Sort the exam slots (date, time) for ordered table display
    sorted_slots = sorted(exam_schedule.keys())

    console = Console()
    table = Table(title="Exam Schedule Comparison")

    # Add columns: Date, Time, then one column per person
    table.add_column("Date")
    table.add_column("Time")
    for person in names:
        table.add_column(person)

    # Define medium-tone colors to assign per date (will cycle if dates exceed colors)
    date_colors = [
        "cyan",           # medium blue
        "green",          # medium green
        "gold3",          # darker gold (not bright yellow)
        "medium_purple3", # medium purple
        "deep_sky_blue4", # deep sky blue (a bit darker)
        "magenta",        # medium magenta
    ]

    # Create a mapping from each unique date to a specific color
    unique_dates = sorted({date for date, _ in sorted_slots})
    date_color_map = {date: date_colors[i % len(date_colors)] for i, date in enumerate(unique_dates)}

    # Populate the table rows
    for date, time in sorted_slots:
        row = []
        color = date_color_map[date]

        # Color date and time columns
        row.append(f"[{color}]{date}[/{color}]")
        row.append(f"[{color}]{time}[/{color}]")

        # Dictionary of {person: course} for quick lookup
        attendees = exam_schedule[(date, time)]
        attendance_dict = {person: course for person, course in attendees}

        # Add each person's exam for this slot, colored by the date's assigned color
        for person in names:
            course = attendance_dict.get(person, "")
            if course:
                row.append(f"[{color}]{course}[/{color}]")
            else:
                row.append("")

        table.add_row(*row)

    # Print the nicely formatted table
    console.print(table)