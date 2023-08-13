from extract_timetable import see_table, create_timetable_list, create_excel_timetable
from ntu_ics_generator import generate_ics_file

generate_ics_file("STARS_NAME.html","14/08/2023")

### TEST EXAMPLES ###

## Produce the processed data used from NTU STARS Planner ##
#test_data = create_timetable_list("STARS_NAME.html")
#see_table(test_data)

## Create an excel file for NTU STARS Planner ##
#create_excel_timetable("STARS_NAME.html")

## Create .ics file for NTU STARS Planner (Outlook, Google Calendar, etc)
# Requires file name (STAR Planner Html) & first day of first teaching week of semester ***
#generate_ics_file("STARS_NAME.html","14/08/2023")



