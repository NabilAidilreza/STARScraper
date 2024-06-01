import os
from ntu_hub import compare_grp_timetables,create_timetable_list
from ntu_ics_generator import generate_ics_file

#! FILE FOR LOCAL EXECUTION OF CODES #

def main():
    #? SETTINGS #
    start_date = "15/08/2024"
    target_folder = "YR1S2"

    #! ICS GENERATOR #
    # target_file_name = "STARS_TEST.html"
    # target_path = target_folder + "\\" + target_file_name
    # generate_ics_file(target_path,start_date)

    #! COMPARE TIMETABLES #
    curr_dir = os.getcwd()
    path = curr_dir + "\\" + target_folder
    dir_list = os.listdir(path)
    for i in range(len(dir_list)):
        dir_list[i] = f"{target_folder}\\" + dir_list[i]
    gen = compare_grp_timetables(dir_list,8,start_date) # => list of html, week, startdate

if __name__ == "__main__":
    main()
