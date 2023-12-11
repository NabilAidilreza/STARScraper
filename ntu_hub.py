from ntu_extract_timetable import print_table, create_timetable_list, compile_mods, get_today, get_weekly, get_course_info, get_all_mods, check_what_week_day,generate_timeline, combine_NTU_dict
from ntu_ics_generator import generate_ics_file
from ntu_compare_timetables import compare_grp_timetables

#generate_ics_file("STARS_FAZ.html","14/08/2023")

#TIMETABLES_TO_COMPARE = ["STARS_NAB.html","STARS_JX.html","STARS_FAZ.html","STARS_TIM.html","STARS_ASH.html","STARS_YJ.html","STARS_ZY.html"]
# Creates a text table to compare timetables -> input -> array of file names (STARS HTML), int week number of semester desired e.g Week 3
#compare_grp_timetables(TIMETABLES_TO_COMPARE,11)

# Execute commands here #