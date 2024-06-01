# from ntu_extract_timetable import print_table, create_timetable_list, compile_mods, get_today, \
#     get_weekly, get_course_info, get_all_mods, check_what_week_day,generate_timeline, combine_NTU_dict

import os
import shutil
import pathlib
from random import randint
from rich.highlighter import Highlighter
from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree

#! Other functions and Rich Functions #

class RainbowHighlighter(Highlighter):
    def highlight(self, text):
        for index in range(len(text)):
            text.stylize(f"color({randint(16, 255)})", index, index + 1)

def make_dir_tree(directory):
    tree = Tree(
        f":open_file_folder: [link file://{directory}]{directory}",
        guide_style="bold bright_blue",
    )
    return tree

def walk_directory(directory: pathlib.Path, tree: Tree) -> None:
    """Recursively build a Tree with directory contents."""
    file_names = []
    # Sort dirs first then by filename
    paths = sorted(
        pathlib.Path(directory).iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )
    for path in paths:
        # Remove hidden files
        if path.name.startswith("."):
            continue
        if path.is_dir():
            style = "dim" if path.name.startswith("__") else ""
            branch = tree.add(
                f"[bold magenta]:open_file_folder: [link file://{path}]{escape(path.name)}",
                style=style,
                guide_style=style,
            )
            walk_directory(path, branch)
        else:
            file_names.append(path.name)
            text_filename = Text(path.name, "green")
            text_filename.highlight_regex(r"\..*$", "bold red")
            text_filename.highlight_regex(r"STARS_", "bold blue_violet")
            text_filename.stylize(f"link file://{path}")
            file_size = path.stat().st_size
            text_filename.append(f" ({decimal(file_size)})", "blue")
            icon = "🗃️ " if path.suffix == ".html" else "📄 "
            tree.add(Text(icon) + text_filename)
    return file_names

def delete_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def delete_files_in_output_folders():
    current_directory = os.getcwd()
    folder1 = os.path.join(current_directory, 'comparison_tables')
    folder2 = os.path.join(current_directory, 'calendars')

    if not os.path.exists(folder1) or not os.path.exists(folder2):
        print("One or both folders do not exist in the current directory.")
        return
    delete_files_in_folder(folder1)
    delete_files_in_folder(folder2)