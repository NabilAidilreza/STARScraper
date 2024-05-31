
# NTU STARS Project

## Desciption

Nanyang Technological University (NTU)

A python program that extracts your modules and timings from a HTML copy of your NTU STARs Timetable. 

## Main functions

- Generates an .ics file (calendar file) to use on Outlook / Google Calendar for better viewing.

- Compare STARS timetable between people / friends.

## Instructions

1. Clone this project

2. Install requirements.txt in command line
```bash
pip install -r requirements.txt
```
3. Download your version of STARS Planner HTML (& your friends, if applicable) [Refer to samples/STARS_SAMPLE.html]

4. Make sure all files are under the same directory.

5. Open *local_commands.py*

run  

```bash
  generate_ics_file("STARS_YOURFILENAME.html","14/08/2023",False)
```
to generate the calender file.

run
```bash
  TIMETABLES_TO_COMPARE = ["STARS_NAME.html","STARS_NAME1.html",...]
  compare_grp_timetables(TIMETABLES_TO_COMPARE,3,False) # Week 3 Comparison, Rich Module off
```
to generate text table output for comparison (> 1 STARS HTML file required)

## Disclaimer

Only available in Python. 

To download required library dependencies on your own computer.

Refer to requirements.txt.

## Extra Notes

#### Python Rich module

Enable the last parameter to True, if you wish to use the Rich library for prettier output.

#### File Naming

DO RENAME YOUR HTML FILE to "STARS_{placeholder}.html" and write the correct file name so that program can run.

#### Start Date

DO CHANGE Start Date (e.g 14/08/2023) such that it will follow the correct calendar sequence based on which sem you are in. (i.e Freshmen Sem 2 YR23/24 -> 15 Jan 2024 etc)

#### Color Coding for ICS file

Categories have been set to respective course code. (e.g Category -> IE1005 [Metadata])

If you want to color code, go to your calender app (e.g Outlook) to set the color to the respective course code (i.e IE1005 -> Blue Category)


