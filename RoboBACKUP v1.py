import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import time


# Function to save the selected source paths to a file
def save_sources_to_file():
    with open("C:\Windows\Temp\saved_sources.txt", "w") as file:
        for item in source_listbox.get(0, tk.END):
            file.write("%s\n" % item)


# Function to save the selected destination path to a file
def save_destination_to_file():
    with open("C:\Windows\Temp\saved_destination.txt", "w") as file:
        file.write(dest_entry.get())


# Function to load saved source paths from a file
def load_sources_from_file():
    try:
        with open("C:\Windows\Temp\saved_sources.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                source_listbox.insert(tk.END, line.strip())
    except FileNotFoundError:
        pass


# Function to load saved destination path from a file
def load_destination_from_file():
    try:
        with open("C:\Windows\Temp\saved_destination.txt", "r") as file:
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


def update_progress(label, progress_var):
    def close_message_box():
        messagebox.showinfo("Backup Completed", "Backup is completed.")
        root.destroy()

    while not progress_var["finished"]:
        label.config(text=f"Backup in progress... {progress_var['value']}%")
        time.sleep(1)

    label.config(text="Backup completed.")
    threading.Thread(target=close_message_box).start()


def start_backup():
    running_window = show_running_message()

    destination_path = dest_entry.get()
    options = "/E /REG /XJ"

    sources = source_listbox.get(0, tk.END)

    backup_root = os.path.join(destination_path, "")

    # Create the backup destination folder if it doesn't exist
    if not os.path.exists(backup_root):
        os.makedirs(backup_root)

    progress_var = {"value": 0, "finished": False}

    def run_backup():
        total_sources = len(sources)
        for idx, source_path in enumerate(sources):
            backup_destination = os.path.join(backup_root, os.path.basename(source_path))

            robocopy_command = f'robocopy "{source_path}" "{backup_destination}" {options}'

            try:
                subprocess.run(robocopy_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except Exception as e:
                messagebox.showerror("Robocopy Error", f"An error occurred for '{source_path}': {e}")

            progress_var["value"] = int((idx + 1) / total_sources * 100)

        progress_var["finished"] = True

    threading.Thread(target=run_backup).start()
    threading.Thread(target=update_progress, args=(status_label, progress_var)).start()


# Create the main window
root = tk.Tk()
root.title("RoboBackup")

# Set the window dimensions
window_width = 800
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_pos = (screen_width - window_width) // 2
y_pos = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

# Create UI elements
source_label = tk.Label(root, text="Source Paths:")
source_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=80)  # Double the width

load_sources_from_file()

add_button = tk.Button(root, text="Add Source", command=browse_source)
remove_button = tk.Button(root, text="Remove Source", command=remove_source)

dest_label = tk.Label(root, text="Destination Path:")
dest_entry = tk.Entry(root)
browse_dest_button = tk.Button(root, text="Browse", command=browse_destination)

load_destination_from_file()

start_button = tk.Button(root, text="Start Backup", command=start_backup)
status_label = tk.Label(root, text="", fg="green")

# Arrange UI elements using grid layout
source_label.grid(row=0, column=0)
source_listbox.grid(row=0, column=1, rowspan=3)

add_button.grid(row=1, column=2)
remove_button.grid(row=2, column=2)

dest_label.grid(row=3, column=0)
dest_entry.grid(row=3, column=1)
browse_dest_button.grid(row=3, column=2)

start_button.grid(row=4, columnspan=3)
status_label.grid(row=5, columnspan=3)

# Copyright label
copyright_label = tk.Label(root, text="© by K. Bussard", anchor="se")
copyright_label.grid(row=6, column=2, sticky="se", padx=10, pady=10)

root.mainloop()
