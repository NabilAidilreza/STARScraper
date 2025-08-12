import os
import sys
import shutil
import json
import pathlib
import webbrowser
from scripts import *
from rich.theme import Theme
from rich.console import Console
from rich.traceback import install
from InquirerPy import prompt
from time import sleep
install()

#! FILE FOR LOCAL EXECUTION OF CODES #

def main():

    #? INIT SETTINGS #
    try:
        with open("settings.json","r") as file:
            init_settings = json.load(file)
            start_date = init_settings["start_date"]
            target_folder = init_settings["target_folder"]
    except Exception:
        init_settings = {
            "start_date": "15/01/2025",
            "target_folder": "TestFolder"
        }
        with open("settings.json", "w") as file:
            json.dump(init_settings, file)
            file.close()
        start_date = init_settings["start_date"]
        target_folder = init_settings["target_folder"]

    def update_settings(new_t="",new_s = ""):
        with open("settings.json","r") as file:
            init_settings = json.load(file)
            if new_t != "":
                init_settings["target_folder"] = new_t
            if new_s != "":
                init_settings["start_date"] = new_s
            file.close()
        with open("settings.json", "w") as file:
            json.dump(init_settings, file)
            file.close()

    #! Main Console #
    custom_theme = Theme({"green":"bold green","yellow":"yellow","cyan":"bold bright_cyan","red":"bold red","magenta":"bold bright_magenta","violet":"bold blue_violet"})
    console = Console(theme=custom_theme)

    console.print("  _________________________ __________  _________ \n\
 /   _____/\__    ___/  _  \\______   \/   _____/ ________________  ______   ___________ \n\
 \_____  \   |    | /  /_\  \|       _/\_____  \_/ ___\_  __ \__  \ \____ \_/ __ \_  __ \\\n\
 /        \  |    |/    |    \    |   \/        \  \___|  | \// __ \|  |_> >  ___/|  | \/\n\
/_______  /  |____|\____|__  /____|_  /_______  /\___  >__|  (____  /   __/ \___  >__|   \n\
        \/                 \/       \/        \/     \/           \/|__|        \/      ")

    console.print("\t\t\t===== [green]NTU STARS Project[/green] =====\n",style="blue")
    console.print("Start date: ",start_date,style="yellow")
    console.print("[yellow]Current target folder:[/yellow] " + f"[cyan]{target_folder}[/cyan]")

    #! CHECK SETUP #
    try:
        curr_dir = os.getcwd()
        path = curr_dir + "\\" + target_folder
        dir_list = os.listdir(path)
        for i in range(len(dir_list)):
            dir_list[i] = f"{target_folder}\\" + dir_list[i]
    except Exception:
        console.print("Folder not found!!!",style="red")
        rainbow = RainbowHighlighter()
        console.print("\nMake new target folder? '" + target_folder + "'",style="yellow")
        option = input("Y/N: ")
        if option.upper() == "Y":
            current_directory = os.path.dirname(os.path.abspath(__file__))
            new_folder_path = os.path.join(current_directory, target_folder)
            os.makedirs(new_folder_path)
            os.system('cls')
            return main()
        else:
            console.print("\nPlease set to an existing folder...",style="yellow")
            console.print("[red]Warning:[/red]" + " Make sure target folder in same directory as project folder.")
            target_name = input("Folder name: ")
            update_settings(target_name,"")
            os.system('cls')
            return main()

    directory = os.path.abspath(target_folder)
    tree = make_dir_tree(directory)
    file_names = walk_directory(pathlib.Path(directory), tree)
    console.print(tree)

    console.print("\nOptions\n\
    1. [green]Generate ics file[/green]\n\
    2. [yellow]Compare timetables[/yellow]\n\
    3. [violet]View generated tables[/violet]\n\
    4. [blue]Check exam schedules[/blue]\n\
    5. [magenta]Delete old files[/magenta]\n\
    6. [cyan]Change settings[/cyan]\n\
    7. [red]Exit[/red]\n\
    Input 'clr' to clear console\n")
    while True:
        choice = input("Input: ")
        if choice == "1":
            target_file_name = prompt({"message": "Target file name: ",
                "type": "fuzzy",
                "choices": file_names})
            target_path = target_folder + "\\" + target_file_name[0]
            generate_ics_file(target_path,start_date)
        elif choice == "2":
            wk = input("Week: ")
            gen = compare_grp_timetables(dir_list,int(wk),start_date)
        elif choice == "3":
            directory = os.path.abspath("comparison_tables")
            tree = make_dir_tree(directory)
            table_names = walk_directory(pathlib.Path(directory), tree)
            if table_names:
                target_table = prompt({"message": "Table: ",
                    "type": "fuzzy",
                    "choices": table_names})
                webbrowser.open("comparison_tables\\"+target_table[0])
            else:
                console.print("No tables detected.",style="red")
        elif choice == "4":
            check_exam_schedules(dir_list,start_date)
        elif choice == "5":
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
        elif choice == "6":
            options = ["Change target folder","Change start date","Delete existing folder","Exit"]
            prompt_option = prompt({"message": "Options: ",
                "type": "fuzzy",
                "choices": options})
            chosen_option = prompt_option[0]
            if chosen_option == "Change target folder":
                new_target_folder = input("New target folder name: ")
                update_settings(new_target_folder,"")
                console.print("[yellow]Target folder set to [/yellow]" + f"[green]{new_target_folder}[/green]")
                console.print("Input 'clr' to refresh page.")
            if chosen_option == "Change start date":
                new_start_date = input("New start date: ")
                update_settings("",new_start_date)
                console.print("[yellow]Start Date set to [/yellow]" + f"[green]{new_start_date}[/green]")
                console.print("Input 'clr' to refresh page.")
            if chosen_option == "Delete existing folder":
                existing_folder_name = input("Folder name: ")
                try:
                    current_directory = os.path.dirname(os.path.abspath(__file__))
                    folder_path = os.path.join(current_directory, existing_folder_name)
                    try:
                        os.rmdir(folder_path)
                    except Exception:
                        shutil.rmtree(folder_path)
                    console.print("Folder '" + existing_folder_name + "'" + " deleted.",style="red")
                except Exception:
                    console.print("Unable to delete folder.",style="red")
                console.print("Input 'clr' to refresh page.")
            if chosen_option == "Exit":
                console.print("Operation aborted.",style="red")
        elif choice == "7":
            for i in range(3,0,-1):
                console.print(f"Exiting program in {i}...",end="\r",style="red")
                sleep(1)
            break
        elif choice.lower() == "clear" or choice.lower() == "clr":
            os.system('cls')
            return main()
    sys.exit()

if __name__ == "__main__":
    main()
