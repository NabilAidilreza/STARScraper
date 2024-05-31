from ntu_hub import compare_grp_timetables,create_timetable_list
from ntu_ics_generator import generate_ics_file
# from rich.traceback import install
# install()

#! FILE FOR LOCAL EXECUTION OF CODES #


# Execute commands here #
import os

# path = "YOUR_PATH/FolderofHTMLS"
# dir_list = os.listdir(path)
# for i in range(len(dir_list)):
#     dir_list[i] = "FolderofHTMLS\\" + dir_list[i]

# gen = compare_grp_timetables(dir_list,8,"15/01/2024") => list of html, week, startdate


#! Examples #

#generate_ics_file("STARS_SAMPLE.html","14/08/2023") => Params: File Name and Start Date of Semester

#TIMETABLES_TO_COMPARE = ["STARS_NAB.html","STARS_JX.html","STARS_FAZ.html","STARS_TIM.html","STARS_YJ.html","STARS_ZY.html"] => List of friends htmls

# Creates a text table to compare timetables -> input -> array of file names (STARS HTML), int week number of semester desired e.g Week 3
#compare_grp_timetables(TIMETABLES_TO_COMPARE,2,"15/01/2024")
