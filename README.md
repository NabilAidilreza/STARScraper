# NTU_Timetable_Generator_Python
 Takes in STARS Planner Html and converts to excel / .ics file for better viewing.

 Only work for Sem 1 (for now), unsure how html will change. (freshman)

 Only available in Python.
 To download required libraries on your own computer. e.g icalendar, bs4, etc.

 # INSTRUCTIONS #
 Download your version of STARS Planner HTML and all 3 python files.
 
 Open menu.py and run generate_ics_file("STARS_NAME.html","14/08/2023") line to generate the file.

 Make sure all files are under the same directory.

 # NOTE #
 DO RENAME YOUR HTML FILE to "STARS_{placeholder}.html" so program can run.

 DO CHANGE Start Date (14/08/2023) such that it will follow the correct calendar sequence based on which sem you are in. (I.E Freshmen Sem 2 -> 15 Jan 2024 etc)
 
 Categories have been set to respective course code. (e.g Category -> IE1005 [Metadata])

 If you are going to color code, go to the calender app (Outlook) to set the color to the course code (i.e IE1005 -> Blue Category)
