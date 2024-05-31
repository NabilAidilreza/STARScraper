
# NTU Timetable Generator

## Desciption

A python program that extracts your modules and timings from a HTML copy of your NTU STARs Timetable.

## Disclaimer

Only available in Python. 

To download required library dependencies on your own computer.

Refer to requirements.txt.

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

4. Save your files under a folder in the same directory.

5. Open *local_commands.py*

6. Edit the following settings

```bash
    start_date = "15/08/2024" # Start Date of Current Semester
    target_folder = "YR1S2"   # Target folder holding all your html files
```

7. In *local_commands.py*

run  

```bash
    target_file_name = "STARS_YOURNAME.html"
    target_folder = "YR1S2"
    target_path = target_folder + "\\" + target_file_name
    generate_ics_file(target_path,start_date)
```
to generate the calender file.

run
```bash
    curr_dir = os.getcwd()
    path = curr_dir + "\\" + target_folder
    dir_list = os.listdir(path)
    for i in range(len(dir_list)):
        dir_list[i] = f"{target_folder}\\" + dir_list[i]
    gen = compare_grp_timetables(dir_list,3,start_date) # Week 3

```
to generate text table output for comparison (> 1 STARS HTML file required)

## NOTE


#### File Naming

DO RENAME YOUR HTML FILE to "STARS_{placeholder}.html" and write the correct file name so that program can run.

#### Start Date

DO CHANGE Start Date (e.g 14/08/2023) such that it will follow the correct calendar sequence based on which sem you are in. (i.e Freshmen Sem 2 YR23/24 -> 15 Jan 2024 etc)

#### Color Coding for ICS file

Categories have been set to respective course code. (e.g Category -> IE1005 [Metadata])

If you want to color code, go to your calender app (e.g Outlook) to set the color to the respective course code (i.e IE1005 -> Blue Category)


