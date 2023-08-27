import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import threading
import time

def save_sources_to_file():
    with open("C:\\Windows\\Temp\\saved_sources.txt", "w") as file:
        for item in source_listbox.get(0, tk.END):
            file.write("%s\n" % item)

def save_destination_to_file():
    with open("C:\\Windows\\Temp\\saved_destination.txt", "w") as file:
        file.write(dest_entry.get())

def load_sources_from_file():
    try:
        with open("C:\\Windows\\Temp\\saved_sources.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                source_listbox.insert(tk.END, line.strip())
    except FileNotFoundError:
        pass

def load_destination_from_file():
    try:
        with open("C:\\Windows\\Temp\\saved_destination.txt", "r") as file:
            dest_entry.insert(0, file.read().strip())
    except FileNotFoundError:
        pass

def browse_source():
    selected_path = filedialog.askdirectory()
    if selected_path:
        source_listbox.insert(tk.END, selected_path)
        save_sources_to_file()

def browse_destination():
    selected_path = filedialog.askdirectory()
    if selected_path:
        dest_path = os.path.join(selected_path, "")
        dest_entry.delete(0, tk.END)
        dest_entry.insert(0, dest_path)
        save_destination_to_file()

def remove_source():
    selected_indices = source_listbox.curselection()
    for idx in reversed(selected_indices):
        source_listbox.delete(idx)
    save_sources_to_file()

def show_running_message():
    running_window = tk.Toplevel(root)
    running_window.title("Running")
    message_label = tk.Label(running_window, text="Backup is currently running, Please Wait...", padx=20, pady=20)
    message_label.pack()
    return running_window

def update_progress(label, progress_var, running_window):
    def close_message_box():
        messagebox.showinfo("Backup Completed", "Backup is completed. \nPlease Close window when finished and safely remove your Backup Storage")
        running_window.destroy()

    while not progress_var["finished"]:
        label.config(text=f"Backup in progress... {progress_var['value']}%")
        time.sleep(1)

    label.config(text="Backup completed.")
    threading.Thread(target=close_message_box).start()

def start_backup():
    running_window = show_running_message()

    destination_path = dest_entry.get()
    options = ""

    sources = source_listbox.get(0, tk.END)
    backup_root = os.path.join(destination_path, "")

    if not os.path.exists(backup_root):
        os.makedirs(backup_root)

    progress_var = {"value": 0, "finished": False}
    total_sources = len(sources)

    threads = []

    def run_backup(source_path, backup_destination, idx):
        selected_options = [option for option, info in checkboxes.items() if info["var"].get() == 1]
        source_name = os.path.basename(source_path)

        # Define the log file path in the root of the destination folder
        log_file = os.path.join(destination_path, f"RoboBACKUP_{source_name}.log")

        robocopy_command = [
                               "robocopy",
                               rf'"{source_path}"',
                               rf'"{backup_destination}"'
                           ] + selected_options

        if save_log_var.get() == 1:
            robocopy_command.append(rf'>> "{log_file}"')

        full_command = " ".join(robocopy_command)
        print("Generated command:", full_command)

        try:
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()  # Capture stdout and stderr

            if process.returncode != 0:
                error_message = f"An error occurred for '{source_path}':\n\n{stderr}"
                # You can choose not to show the messagebox here
            else:
                print(f"Backup completed for '{source_path}'\n\n{stdout}")

        except Exception as e:
            # You can choose not to show the messagebox here
            pass

        # Suppress printing of stderr
        with open(os.devnull, 'w') as devnull:
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=devnull,
                universal_newlines=True
            )
            stdout, _ = process.communicate()

        progress_var["value"] = int((idx + 1) / total_sources * 100)

    for idx, source_path in enumerate(sources):
        backup_destination = os.path.join(backup_root, os.path.basename(source_path))
        thread = threading.Thread(target=run_backup, args=(source_path, backup_destination, idx))
        thread.start()
        threads.append(thread)

    def check_threads():
        for thread in threads:
            if thread.is_alive():
                root.after(1000, check_threads)
                return
        progress_var["finished"] = True
        update_progress(status_label, progress_var, running_window)

    check_threads()

def get_selected_options():
    selected_options = [option for option, info in checkboxes.items() if info["var"].get() == 1]
    selected_command.set(f'robocopy "source" "destination" {" ".join(selected_options)} 2>&1')

def generate_robocopy_command(source, destination):
    selected_options = [option for option, info in checkboxes.items() if info["var"].get() == 1]

    robocopy_command = [
        "robocopy",
        source,
        destination
    ] + selected_options

    if save_log_var.get() == 1:
        log_file = os.path.join(destination, "RoboBACKUP.log")
        robocopy_command.append(f'>> "{log_file}"')

    command = " ".join(robocopy_command)
    print("Generated command:", command)
    return command



def update_command_label():
    sources = source_listbox.get(0, tk.END)
    destination = dest_entry.get()

    if not sources:
        command = 'robocopy "source" "destination"'
    else:
        commands = []
        for source_path in sources:
            command = generate_robocopy_command(source_path, destination)
            commands.append(command)
        command = "\n".join(commands)  # Add line breaks between commands

    selected_command.set(command)


root = tk.Tk()
root.title("RoboBackup v1.5")

window_width = 720
window_height = 630
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_pos = (screen_width - window_width) // 2
y_pos = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

main_tab = tk.Frame(notebook)
notebook.add(main_tab, text="Main")

source_label = tk.Label(main_tab, text="Source Paths:")
source_listbox = tk.Listbox(main_tab, selectmode=tk.MULTIPLE, width=80)
load_sources_from_file()

add_button = tk.Button(main_tab, text="Add Source", command=browse_source)
remove_button = tk.Button(main_tab, text="Remove Source", command=remove_source)

dest_label = tk.Label(main_tab, text="Destination Path:")
dest_entry = tk.Entry(main_tab, width=80)
browse_dest_button = tk.Button(main_tab, text="Browse", command=browse_destination)
load_destination_from_file()

save_log_var = tk.IntVar(value=0)  # Variable to track the state of the "Save log at destination" checkbox

# Checkbox to enable/disable saving log
save_log_checkbox = tk.Checkbutton(main_tab, text="Save log at destination", variable=save_log_var)
save_log_checkbox.grid(row=8, column=0, columnspan=3, sticky="w")

start_button = tk.Button(main_tab, text="Start Backup", command=start_backup)
status_label = tk.Label(main_tab, text="", fg="green")

source_label.grid(row=0, column=0)
source_listbox.grid(row=0, column=1, rowspan=3)

add_button.grid(row=1, column=2)
remove_button.grid(row=2, column=2)

dest_label.grid(row=3, column=0)
dest_entry.grid(row=3, column=1)
browse_dest_button.grid(row=3, column=2)

start_button.grid(row=4, columnspan=3)
status_label.grid(row=5, columnspan=3)

options_frame = tk.Frame(main_tab)
options_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")

checkboxes = {
    "/e": {"var": tk.IntVar(value=1), "desc": "Copy files and subdirectories, including Empty ones DEFAULT"},
    "/reg": {"var": tk.IntVar(value=1), "desc": "Copy with file security (equivalent to /COPY:DATS) DEFAULT"},
    "/xj": {"var": tk.IntVar(value=1), "desc": "Exclude junction points (typically for symbolic links) DEFAULT"},
    "/s": {"var": tk.IntVar(), "desc": "Copy subdirectories, but not Empty ones"},
    "/mir": {"var": tk.IntVar(), "desc": "Mirror a directory tree"},
    "/compress": {"var": tk.IntVar(), "desc": "Requests network compression, if applicable"},
    # Add more options here...
}

default_label = tk.Label(main_tab, text="DEFAULT IS FOR FULL INITIAL BACKUP + DIFFERENTIAL BACKUP if ran again with the same Source / Destination", padx=10, pady=10, wraplength=600, justify="left")
default_label.grid(row=10, column=0, columnspan=3, sticky="w")

for option, info in checkboxes.items():
    checkbox = tk.Checkbutton(options_frame, text=option + "  " + info["desc"], variable=info["var"], command=update_command_label)
    checkbox.pack(anchor="w", padx=10, pady=(0, 5))

selected_command = tk.StringVar(value='robocopy "source" "destination"')
command_label = tk.Label(main_tab, textvariable=selected_command, wraplength=600, justify="left")
command_label.grid(row=7, column=0, columnspan=3, padx=10, sticky="w")


update_command_label()  # Call initially to set the default command

get_options_button = tk.Button(main_tab, text="Get Selected Options", command=lambda: [get_selected_options(), update_command_label()])
get_options_button.grid(row=9, column=0, columnspan=3, pady=10)

copyright_label = tk.Label(root, text="©2023 by K. Bussard", anchor="se")
copyright_label.pack(side="bottom", padx=10, pady=10)

root.mainloop()