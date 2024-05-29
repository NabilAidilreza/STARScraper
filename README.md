
# NTU_Timetable_Generator

## Disclaimer

Only available in Python. To download required libraries on your own computer. e.g icalendar, bs4, etc.

## Purpose

Generates an .ics file (calendar file) to use on Outlook / Google Calendar for better viewing.

Compare STARS timetable between people / friends.

## Instructions

Download your version of STARS Planner HTML (& your friends, if applicable) and all python files.

Make sure all files are under the same directory.

Open *local_commands.py* and run  

```bash
  generate_ics_file("STARS_NAME.html","14/08/2023")
```
to generate the calender file.

run
```bash
  TIMETABLES_TO_COMPARE = ["STARS_NAME.html","STARS_NAME1.html",...]
  compare_grp_timetables(TIMETABLES_TO_COMPARE,3)
```
to generate text table output for comparison (> 1 STARS HTML file required)

## IMPORTANT

#### File Naming

DO RENAME YOUR HTML FILE to "STARS_{placeholder}.html" and change generate_ics_file var to correct file name so program can run.

#### Start Date

DO CHANGE Start Date (e.g 14/08/2023) such that it will follow the correct calendar sequence based on which sem you are in. (i.e Freshmen Sem 2 -> 15 Jan 2024 etc)

#### Color Coding

Categories have been set to respective course code. (e.g Category -> IE1005 [Metadata])

If you are going to color code, go to the calender app (Outlook) to set the color to the course code (i.e IE1005 -> Blue Category)


