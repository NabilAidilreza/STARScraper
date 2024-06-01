import os
import json
import pathlib
from scripts import *
from rich.theme import Theme
from rich.console import Console
from rich.traceback import install
install()

#! FILE FOR LOCAL EXECUTION OF CODES #

def main():

    #? SETTINGS #
    try:
        with open("settings.json","r") as file:
            init_settings = json.load(file)
            start_date = init_settings["start_date"]
            target_folder = init_settings["target_folder"]
    except Exception:
        init_settings = {
            "start_date": "15/08/2024",
            "target_folder": "TestFolder"
        }
        with open("settings.json", "w") as file:
            json.dump(init_settings, file)
            file.close()
        start_date = init_settings["start_date"]
        target_folder = init_settings["target_folder"]


    #! Main Console #
    custom_theme = Theme({"green":"bold green","yellow":"yellow","cyan":"bold bright_cyan","red":"bold red","magenta":"bold bright_magenta","violet":"bold blue_violet"})
    console = Console(theme=custom_theme)

    console.print("--- [green]NTU STARS Project[/green] ---\n",style="blue")
    console.print("Start date: ",start_date,style="yellow")
    console.print("[yellow]Current target folder:[/yellow] " + f"[cyan]{target_folder}[/cyan]")

    #! INIT SETUP #
    try:
        curr_dir = os.getcwd()
        path = curr_dir + "\\" + target_folder
        dir_list = os.listdir(path)
        for i in range(len(dir_list)):
            dir_list[i] = f"{target_folder}\\" + dir_list[i]
    except Exception:
        console.print("Folder not found!!!",style="red")
        console.print("Please set to the correct folder...",style="yellow")
        target_name = input("Folder name: ")
        with open("settings.json","r") as file:
            init_settings = json.load(file)
            init_settings["target_folder"] = target_name
            file.close()
        with open("settings.json", "w") as file:
            json.dump(init_settings, file)
            file.close()
        console.print("[yellow]Target folder set to [/yellow]" + f"[green]{target_name}[/green]")
        os.system('cls')
        return main()

    directory = os.path.abspath(target_folder)
    tree = make_dir_tree(directory)
    walk_directory(pathlib.Path(directory), tree)
    console.print(tree)
    rainbow = RainbowHighlighter()
    console.print(rainbow("\nMake sure target folder in same directory in project folder.\n"))

    console.print("Options\n\
    1. [green]Generate ics file[/green]\n\
    2. [yellow]Compare timetables[/yellow]\n\
    3. [magenta]Delete old files[/magenta]\n\
    4. [cyan]Change target folder[/cyan]\n\
    5. [violet]Change start date[/violet]\n\
    6. [red]Exit[/red]\n\
    Input 'clr' to clear console\n")
    while True:
        choice = input("Input: ")
        if choice == "1":
            target_file_name = input("Target file name: ")
            target_path = target_folder + "\\" + target_file_name
            generate_ics_file(target_path,start_date)
        elif choice == "2":
            wk = input("Week: ")
            gen = compare_grp_timetables(dir_list,int(wk),start_date)
        elif choice == "3":
            folders = ["calendars","comparison_tables"]
            for folder in folders:
                directory = os.path.abspath(folder)
                tree = make_dir_tree(directory)
                walk_directory(pathlib.Path(directory), tree)
                console.print(tree)
            confirmation = input("Delete old files? (y/n): ")
            if confirmation.lower() == "y":
                delete_files_in_output_folders()
                console.print("[green]Files deleted successfuly.[/green]")
            else:
                console.print("[red]Operation aborted.[/red]")
        elif choice == "4":
            new_target_folder = input("New target folder name: ")
            with open("settings.json","r") as file:
                init_settings = json.load(file)
                init_settings["target_folder"] = new_target_folder
                file.close()
            with open("settings.json", "w") as file:
                json.dump(init_settings, file)
                file.close()
            console.print("[yellow]Target folder set to [/yellow]" + f"[green]{new_target_folder}[/green]")
            console.print("Input 'clr' to refresh page.")
        elif choice == "5":
            new_start_date = input("New start date: ")
            with open("settings.json","r") as file:
                init_settings = json.load(file)
                init_settings["start_date"] = new_start_date
                file.close()
            with open("settings.json", "w") as file:
                json.dump(init_settings, file)
                file.close()
            console.print("[yellow]Start Date set to [/yellow]" + f"[green]{new_start_date}[/green]")
            console.print("Input 'clr' to refresh page.")
        elif choice == "6":
            break
        elif choice.lower() == "clear" or choice.lower() == "clr":
            os.system('cls')
            return main()

if __name__ == "__main__":
    main()

# # DEBUGGER #
# generate_ics_file("STARS_FAZ.html","14/08/2023")

# TIMETABLES_TO_COMPARE = ["STARS_NAB.html","STARS_JX.html","STARS_FAZ.html","STARS_TIM.html","STARS_YJ.html","STARS_ZY.html"]
# Creates a text table to compare timetables -> input -> array of file names (STARS HTML), int week number of semester desired e.g Week 3
# compare_grp_timetables(TIMETABLES_TO_COMPARE,2,"15/01/2024")

# for i in range(2,8):
#     gen = compare_grp_timetables(dir_list,i,"15/01/2024")

# generate_ics_file("YR1S2_HTMLS\\STARS_NABIL.html","15/01/2024")

# a = create_timetable_list("YR1S2_HTMLS\\STARS_NABIL.html")
# for week in a:
#     print("Week ",a.index(week),"\n\n")
#     for m in week:
#         print(m)