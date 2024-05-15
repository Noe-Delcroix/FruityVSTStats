import os
from collections import OrderedDict
import json
from datetime import datetime, timedelta
import pyflp
from pyflp.plugin import VSTPlugin
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog


def select_directory():
    """
    Open a file dialog to select the base directory the FLP files are located
    :return: the selected directory path
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring the dialog to the front
    selected_directory = filedialog.askdirectory(
        title="Select the directory containing the FLP files you want to scan"
    )  # Open the dialog
    return selected_directory


def select_save_file():
    """
    Open a file dialog to select the save file path
    :return: the selected file path
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring the dialog to the front
    default_filename = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S") + "_flp_stats.json"  # Default filename with timestamp
    file_path = filedialog.asksaveasfilename(
        defaultextension='.json',
        filetypes=[('JSON files', '*.json')],
        title="Save exported json data as...",
        initialfile=default_filename  # Set default filename
    )
    return file_path


def get_flp_file_paths(base_dir_path):
    """
    Get all the FLP files in the directory, ignoring the "Backup" directories
    :param base_dir_path: the base directory path
    :return: a list of FLP file paths
    """
    flp_files = []
    # Walk through the directory
    for root, dirs, files in os.walk(base_dir_path):
        # Modify the dirs list in-place to skip directories named "backup"
        dirs[:] = [d for d in dirs if d != "Backup"]
        for file in files:
            if file.endswith('.flp'):
                # Construct full file path
                file_path = os.path.join(root, file)
                # Add it to the list
                flp_files.append(file_path)
    return flp_files


def add_vst_plugin_to_stats(flp, flp_path, plugin, stats):
    """
    Add a VST plugin to the stats dictionary
    :param flp: flp project
    :param flp_path: flp file path
    :param plugin: plugin object
    :param stats: stats dictionary
    """
    if not hasattr(plugin, 'name'):
        # print(f"Skipping plugin: {plugin.INTERNAL_NAME}")
        return

    plugin_key = f"{plugin.name} ({plugin.vendor})"
    project_key = flp_path

    if plugin_key in stats:
        if project_key in stats[plugin_key]:
            stats[plugin_key][project_key]["occurrences"] += 1
        else:
            stats[plugin_key][project_key] = {
                "date": flp.created_on,
                "occurrences": 1,
            }
    else:
        stats[plugin_key] = {}
        stats[plugin_key][project_key] = {
            "date": flp.created_on,
            "occurrences": 1,
        }


def get_vst_plugin_list_from_mixer(flp, flp_path, stats):
    """
    Get the VST plugins from the project's mixer tracks (FX plugins)
    :param flp: flp project
    :param flp_path: flp file path
    :param stats: stats dictionary
    """
    for mixer_track in flp.mixer:
        for slot in mixer_track:
            if hasattr(slot, 'plugin') and isinstance(slot.plugin, VSTPlugin):
                add_vst_plugin_to_stats(flp, flp_path, slot.plugin, stats)


def get_vst_plugin_list_from_channels(flp, flp_path, stats):
    """
    Get the VST plugins from the project's channels (instrument plugins)
    :param flp: flp project
    :param flp_path: flp file path
    :param stats: stats dictionary
    :return:
    """
    for channel in flp.channels:
        if hasattr(channel, 'plugin') and isinstance(channel.plugin, VSTPlugin):
            add_vst_plugin_to_stats(flp, flp_path, channel.plugin, stats)


def main():
    """
    Main function
    """
    print("Select the directory containing the FLP files you want to scan")
    base_dir_path = select_directory()
    print(f"Selected directory: {base_dir_path}")

    try:
        flp_file_paths = get_flp_file_paths(base_dir_path)
        if len(flp_file_paths) == 0:
            print("No FLP files found in the selected directory")
            return
        print(f"Found {len(flp_file_paths)} FLP files")
    except Exception as e:
        print(f"Error: {e}")
        return

    global_stats = {}

    total_time_spent = timedelta()
    for file_path in tqdm(flp_file_paths, desc='Processing FLP Files'):
        flp = pyflp.parse(file_path)
        file_name = os.path.basename(file_path)
        get_vst_plugin_list_from_channels(flp, file_name, global_stats)
        get_vst_plugin_list_from_mixer(flp, file_name, global_stats)
        total_time_spent += flp.time_spent

    formated_stats = {
        "scanned_directory": base_dir_path,
        "total_flp_files_scanned": len(flp_file_paths),
        "total_plugins_found": len(global_stats),
        "total_time_spent_on_flp": str(total_time_spent),
        "average_time_spent_on_flp": str(total_time_spent / len(flp_file_paths)),
        "plugins": {}
    }
    for plugin_name, projects in tqdm(global_stats.items(), desc='Generating Output file'):
        formated_stats["plugins"][plugin_name] = {
            "used_in_projects": len(projects),
            "total_times_used": 0,
            "average_uses_in_project": 0,
            "last_time_used": datetime(1970, 1, 1)
        }
        for project, data in projects.items():
            formated_stats["plugins"][plugin_name]["total_times_used"] += data["occurrences"]
            if data["date"] > formated_stats["plugins"][plugin_name]["last_time_used"]:
                formated_stats["plugins"][plugin_name]["last_time_used"] = data["date"]

        # average occurrences
        formated_stats["plugins"][plugin_name]["average_uses_in_project"] = formated_stats["plugins"][plugin_name][
                                                                                "total_times_used"] / \
                                                                            formated_stats["plugins"][plugin_name][
                                                                                "used_in_projects"]
        # convert last date to string
        formated_stats["plugins"][plugin_name]["last_time_used"] = formated_stats["plugins"][plugin_name][
            "last_time_used"].strftime("%Y-%m-%d")

    formated_stats["plugins"] = OrderedDict(sorted(
        formated_stats["plugins"].items(),
        key=lambda item: item[1].get('used_in_projects', 0),
        reverse=True
    ))

    save_location = select_save_file()

    with open(save_location, 'w') as f:
        json.dump(formated_stats, f, indent=4)

    print(f"Data saved to: {save_location}")


if __name__ == "__main__":
    main()
