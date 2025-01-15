import os
from scripts import compare_grp_timetables, generate_ics_file,create_timetable_list

#! FILE FOR LOCAL EXECUTION OF CODES #

def main():
    #? SETTINGS #
    start_date = "13/01/2025"
    target_folder = "YR2S2"

    #! CHECK LIST #
    test = create_timetable_list("STARS_FAZLI.html")
    for i in range(10):
        print(test[1][i])
    # print(len(test))
    #! ICS GENERATOR #
    # target_file_name = "STARS_TEST.html"
    # target_path = target_folder + "\\" + target_file_name
    # generate_ics_file(target_path,start_date)

    #! COMPARE TIMETABLES #
    # curr_dir = os.getcwd()
    # path = curr_dir + "\\" + target_folder
    # dir_list = os.listdir(path)
    # for i in range(len(dir_list)):
    #     dir_list[i] = f"{target_folder}\\" + dir_list[i]
    # gen = compare_grp_timetables(dir_list,8,start_date) # => list of html, week, startdate


    # CTRL /

if __name__ == "__main__":
    main()
