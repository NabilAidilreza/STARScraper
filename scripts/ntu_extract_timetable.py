import os
import re
import csv
import json
from datetime import datetime,timedelta
from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import PatternFill, Font


#! FILE THAT MANAGES ALL BASIC FUNCTIONS OF PROJECT #

### HTML Reader Functions ###

# Opens and read html content from html file #
def read_html_file(file_name):
    # Get the current directory of the script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    main_directory = os.path.dirname(script_directory)
    # Construct the file path by joining the script directory and the file name
    file_path = os.path.join(main_directory, file_name)
    # Open the file in read mode and specify the encoding as utf-8
    with open(file_path, 'r', encoding='windows-1252') as file:
        # Read the content of the file
        html_content = file.read()
        # Return the HTML content
        return html_content

# Convert html content to python list #
def process_html_to_data(FILE_NAME):
    # Set the name of the HTML file to be processed
    file_name = FILE_NAME
    # Read the contents of the HTML file
    html_content = read_html_file(file_name)
    # Create an empty list to store the table data
    table = []
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find the main content section of the HTML
    mainContent = soup.find_all('table')[3]
    # Find all the rows in the main content section
    content_Rows = mainContent.find_all('tr')
    # Iterate over each row in the content_Rows list
    for row in content_Rows:
        # Find all the data cells in the current row
        data = row.find_all('td')
        # Create an empty list to store the processed row data
        temp_row = []
        # Iterate over each data cell in the current row
        for d in data:
            # Process the text by removing newlines
            process_text = d.text.replace('\n','')
            # Replace any '\xa0' with an empty string
            if process_text == '\xa0':
                process_text = ''
            # Append the processed text to the temp_row list
            temp_row.append(process_text)
        # Append the temp_row list (excluding the first element) to the table list
        table.append(temp_row[1:])
    # Fix the last part of the table
    table[-1][0],table[-1][1] = table[-1][1],table[-1][0]
    table[-1][0] = "Total AU Registered"
    table[-1][-1] = ""
    # Return the table data
    #print("Reading HTML...")
    # Output raw data in list form #
    return table

### -------------------------###

### Helper Sorting Functions ###

# Sort by day helper func #
def get_day_number(day):
    # Define a dictionary to map full weekday names to their numeric representation
    days_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    # Extract the abbreviated weekday name from the full name (assuming the first 3 characters represent the abbreviation)
    abbreviated_day = day[:3]
    return days_mapping.get(abbreviated_day,-1)

# Sort by week helper func #
def get_week_from_remark(remark):
    # Remove the 'Teaching Wk' prefix from the remark string
    week_str = remark.replace('Teaching Wk', '').strip()
    # Check if the remaining string is a digit
    if week_str.isdigit():
        # If it is, return a list with that digit as the only element
        return [int(week_str)]
    else:
        # If it's not a digit, return 0
        return 0

### -------------------------###

### Data Filtering Functions ###

# Settle blanks, standarization, general cleaning, sorting #
def process_data(FILE_NAME):
    # Prepare Data #
    file_name = FILE_NAME
    table = []
    table = process_html_to_data(file_name)
    # Fill up blanks #
    for i in range(len(table)):
        for m in range(len(table[i])):
            if table[i][m] == '':
                table[i][m] = table[i-1][m]
    # Clean Last Row #
    table[-1][0],table[-1][1] = table[-1][1],table[-1][0]
    table[-1][0] = "Total AU Registered"
    table[-1][-1] = ""
    course_info = table
    # Clean table #
    course_info = [course for course in course_info if all(course)]
    # Sort by Day #
    sorted_array = sorted(course_info, key=lambda x: (get_day_number(x[11]), x[12]))
    # Returns a sorted array based on raw list provided #
    return sorted_array

# Settle duplicates, filling missing weeks, final cleaning and sorting #
def further_process_data(table):
    course_table = table
    extra_table = []
    to_duplicate = []
    extract_table = course_table[1:]
    # Create duplicates for sorting by week purposes #
    for i in range(len(extract_table)):
        strweeklist = extract_table[i][14]
        weeklist = []
        for ele in strweeklist.strip('Teaching Wk').split(','):
            if '-' in ele:
                weeklist += list(range(*[int(x)+i for i,x in enumerate(ele.split('-'))]))
            else:
                weeklist += [int(ele)]
        to_duplicate.append([i,weeklist])
    # Adjust duplicates #
    for d in to_duplicate:
        temp = []
        for i in range(len(d[1])):
            temp_course = extract_table[d[0]]
            temp.append(temp_course[:14] + ["Teaching Wk"+str(d[1][i])] + temp_course[15:])
        extra_table.append(temp)
    main_table = []
    # Combine all list #
    for e in extra_table:
        for m in e:
            main_table.append(m)
    course_info = main_table
    # Clean table #
    course_info = [course for course in course_info if all(course)]
    # Sort by Week -> Day -> Time #
    sorted_array = sorted(course_info, key=lambda x: (get_week_from_remark(x[14]), get_day_number(x[11]), x[12]))
    sorted_array.insert(0,course_table[0])
    # Break up into different sets (by week) #
    curr = ''
    prev = ''
    final_array = []
    same_week_list = []
    for array in sorted_array:
        curr = array[14]
        if curr != prev:
            prev = curr
            final_array.append(same_week_list)
            same_week_list = []
        same_week_list.append(array)
    if same_week_list != []:
        final_array.append(same_week_list)
        same_week_list = []
    # Clear empty list at the start #
    del final_array[0]
    return final_array

# Creates a python list, fully sorted and cleaned #
def create_timetable_list(FILE_NAME):
    sorted_data = process_data(FILE_NAME)
    final_data = further_process_data(sorted_data)
    return final_data

### -------------------------###

### CSV / Excel Writing Functions ###

def write_timetable_to_csv(data,raw_data):
    #headers = data[0][0]
    headers = ["","Title","ModuleNo","Time","Venue","Group","ClassType","IndexNo","AU","CourseType","S/U","GERType","Status","Choice","Remark","Exam"]
    data = data[1:]
    print("Writing data into Excel...")
    workbook = openpyxl.Workbook()
    ### Create Overview Sheet ###
    workbook.create_sheet(title="Overview")
    sheet = workbook["Overview"]
    for row_idx, row in enumerate(raw_data, start=1):
        for col_idx, cell_value in enumerate(row, start=1):
            sheet.cell(row=row_idx, column=col_idx, value=cell_value)
    # Auto-adjust column width
    for column_cells in sheet.columns:
        max_length = 0
        for cell in column_cells:
            if cell.value is not None:
                max_length = max(max_length, len(str(cell.value)))
        adjusted_width = (max_length + 2) * 1.2  # Adding some buffer space and adjusting
        sheet.column_dimensions[column_cells[0].column_letter].width = adjusted_width
    # Auto-adjust row height
    for row_cells in sheet.rows:
        max_height = 0
        for cell in row_cells:
            if cell.value is not None:
                lines = str(cell.value).count('\n') + 1
                max_height = max(max_height, lines)
        adjusted_height = max_height * 15  # You can adjust the row height as needed
        sheet.row_dimensions[row_cells[0].row].height = adjusted_height
    ### Create Wk 1-13 Sheets ###
    n=13
    week_list = [f'Wk{i}' for i in range(1, n+1)]
    for week_name in week_list:
        workbook.create_sheet(title=week_name)
    # Write data into weeks sheets respectively #
    for week_number, week_name in enumerate(week_list, start=1):
        sheet = workbook[week_name]
        # Write headers to the first row
        for col_idx, header in enumerate(headers, start=1):
            sheet.cell(row=1, column=col_idx, value=header)
        for row_idx, row in enumerate(data[week_number-1], start=2):
            for col_idx, cell_value in enumerate(row, start=1):
                #sheet.cell(row=row_idx, column=col_idx, value=cell_value)
                #order = [12,2,1,13,14,11,10,7,3,4,5,6,8,9,15,16]
                if col_idx == 12:
                    sheet.cell(row=row_idx, column=1, value=cell_value)
                elif col_idx == 2:
                    sheet.cell(row=row_idx, column=2, value=cell_value)
                elif col_idx == 1:
                    sheet.cell(row=row_idx, column=3, value=cell_value)
                elif col_idx == 13:
                    sheet.cell(row=row_idx, column=4, value=cell_value)
                elif col_idx == 14:
                    sheet.cell(row=row_idx, column=5, value=cell_value)
                elif col_idx == 11:
                    sheet.cell(row=row_idx, column=6, value=cell_value)
                elif col_idx == 10:
                    sheet.cell(row=row_idx, column=7, value=cell_value)
                elif col_idx == 7:
                    sheet.cell(row=row_idx, column=8, value=cell_value)
                elif col_idx == 3:
                    sheet.cell(row=row_idx, column=9, value=cell_value)
                elif col_idx == 4:
                    sheet.cell(row=row_idx, column=10, value=cell_value)
                elif col_idx == 5:
                    sheet.cell(row=row_idx, column=11, value=cell_value)
                elif col_idx == 6:
                    sheet.cell(row=row_idx, column=12, value=cell_value)
                elif col_idx == 8:
                    sheet.cell(row=row_idx, column=13, value=cell_value)
                elif col_idx == 9:
                    sheet.cell(row=row_idx, column=14, value=cell_value)
                elif col_idx == 15:
                    sheet.cell(row=row_idx, column=15, value=cell_value)
                elif col_idx == 16:
                    sheet.cell(row=row_idx, column=16, value=cell_value)
        # Optionally, you can set a title for the sheet
        sheet['A1'] = f"Day"
        # Auto-adjust column width
        for column_cells in sheet.columns:
            max_length = 0
            for cell in column_cells:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))
            adjusted_width = (max_length + 2) * 1.2  # Adding some buffer space and adjusting
            sheet.column_dimensions[column_cells[0].column_letter].width = adjusted_width
        # Auto-adjust row height
        for row_cells in sheet.rows:
            max_height = 0
            for cell in row_cells:
                if cell.value is not None:
                    lines = str(cell.value).count('\n') + 1
                    max_height = max(max_height, lines)
            adjusted_height = max_height * 15
            sheet.row_dimensions[row_cells[0].row].height = adjusted_height
    workbook.remove(workbook['Sheet'])
    workbook.save("weekly_data.xlsx")

def write_to_csv():
    table = process_html_to_data()
    with open('Courses.csv', 'w',newline="") as f:
        # create the csv writer
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerows(table)

def color_cells(workbook):
    # Color Coding #
    color_Mon = '538DD5' # light blue
    color_Tue = '76933C' # light 
    color_Wed = 'FABF8F' #
    color_Thurs = 'B1A0C7' #
    color_Fri = '366092' #
    n = 13
    week_list = [f'Wk{i}' for i in range(1, n+1)]
    worksheet = workbook["Overview"]
    for row in worksheet: 
        if row[11].value == "Day":
            for cell in row:
                cell.font = Font(bold=True)
        if row[11].value == "Mon":
            clr_background = PatternFill(start_color='5eb5e9', end_color='5eb5e9', fill_type="solid")
            for cell in row:
                cell.fill = clr_background
        if row[11].value == "Tue":
            clr_background = PatternFill(start_color='4cc249', end_color='4cc249', fill_type="solid")
            for cell in row:
                cell.fill = clr_background
        if row[11].value == "Wed":
            clr_background = PatternFill(start_color='dba658', end_color='dba658', fill_type="solid")
            for cell in row:
                cell.fill = clr_background
        if row[11].value == "Thu":
            clr_background = PatternFill(start_color='eeeb59', end_color='eeeb59', fill_type="solid")
            for cell in row:
                cell.fill = clr_background
        if row[11].value == "Fri":
            clr_background = PatternFill(start_color='0f67b7', end_color='0f67b7', fill_type="solid")
            for cell in row:
                cell.fill = clr_background
    for week in week_list:
        worksheet = workbook[week]
        for row in worksheet: 
            if row[0].value == "Day":
                for cell in row:
                    cell.font = Font(bold=True)
            if row[0].value == "Mon":
                clr_background = PatternFill(start_color='5eb5e9', end_color='5eb5e9', fill_type="solid")
                for cell in row:
                    cell.fill = clr_background
            if row[0].value == "Tue":
                clr_background = PatternFill(start_color='4cc249', end_color='4cc249', fill_type="solid")
                for cell in row:
                    cell.fill = clr_background
            if row[0].value == "Wed":
                clr_background = PatternFill(start_color='dba658', end_color='dba658', fill_type="solid")
                for cell in row:
                    cell.fill = clr_background
            if row[0].value == "Thu":
                clr_background = PatternFill(start_color='eeeb59', end_color='eeeb59', fill_type="solid")
                for cell in row:
                    cell.fill = clr_background
            if row[0].value == "Fri":
                clr_background = PatternFill(start_color='0f67b7', end_color='0f67b7', fill_type="solid")
                for cell in row:
                    cell.fill = clr_background
    # Save the changes back to the Excel file
    workbook.save("weekly_data.xlsx")

def create_excel_timetable(FILE_NAME):
    sorted_data = process_data(FILE_NAME)
    temp = sorted_data
    final_data = further_process_data(sorted_data)
    # Write to Excel #
    write_timetable_to_csv(final_data,temp)
    # Organize in Excel #
    workbook = openpyxl.load_workbook("weekly_data.xlsx")
    color_cells(workbook)
 
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

# Return sem week dates #
def generate_timeline(start_date):
    timeline = []
    num_of_weeks = 14 ### Same for every sem
    sd = start_date.split("/")
    startday = datetime(int(sd[-1]), int(sd[1][1]) if sd[1][0] == "0" else int(sd[1]), int(sd[0]), 0, 0, 0)   
    for i in range(num_of_weeks):
        week = []
        if i == 0:
            continue
        elif i >= 8:
            pass
        else:
            i = i-1
        for j in range(6):
            date = startday + timedelta(days=(7*(i))+j)
            date = date.strftime("%d/%m/%Y")
            week.append(date) # Mon to Sat
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
    test_data = create_timetable_list("STARS_NAB.html")
    test_dict = compile_mods(test_data)
    timeline = generate_timeline("15/01/2024")
    #pretty_print(hello)
    print_timeline(timeline)




