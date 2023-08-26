
# NTU_Timetable_Generator

Generates an .ics file (calendar file) to use on Outlook / Google Calendar for better viewing.


## Disclaimer

Only work for Sem 1 (for now), unsure how html will change. (Im a freshman)

Only available in Python. To download required libraries on your own computer. e.g icalendar, bs4, etc.


## Instructions

Download your version of STARS Planner HTML and all 3 python files.

Make sure all files are under the same directory.

Open *menu.py* and run  

```bash
  generate_ics_file("STARS_NAME.html","14/08/2023")
```
to generate the file.

## IMPORTANT

#### File Naming

DO RENAME YOUR HTML FILE to "STARS_{placeholder}.html" and change generate_ics_file var to correct file name so program can run.

#### Start Date

DO CHANGE Start Date (14/08/2023) such that it will follow the correct calendar sequence based on which sem you are in. (i.e Freshmen Sem 2 -> 15 Jan 2024 etc)

#### Color Coding

Categories have been set to respective course code. (e.g Category -> IE1005 [Metadata])

If you are going to color code, go to the calender app (Outlook) to set the color to the course code (i.e IE1005 -> Blue Category)


## Functions

- Generate .ics file
- Compare timetables (text table)

