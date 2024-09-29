import os
import shutil
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading

macros_path = os.path.join(os.getenv('LOCALAPPDATA'), "GeometryDash", "geode", "mods", "tobyadd.gdh", "Macros")
output_path = os.path.join(".", "Macros")

def copy_files(folder_path, output_path, progress_var, status_label):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    files = os.listdir(folder_path)
    total_files = len(files)
    
    for i, filename in enumerate(files):
        file_path = os.path.join(folder_path, filename)
        output_file_path = os.path.join(output_path, filename)
        
        if os.path.exists(output_file_path):
            if os.path.getsize(file_path) == os.path.getsize(output_file_path):
                status_label.config(text=f"Skipping {filename} as it already exists with the same size.")
                print(f"Skipping {filename} as it already exists with the same size.")
                progress_var.set((i + 1) / total_files * 100)
                root.update_idletasks()
                continue
        
        try:
            shutil.copy(file_path, output_path)
            status_label.config(text=f"Copied {filename} successfully.")
            print(f"Copied {filename} successfully.")
        except Exception as e:
            status_label.config(text=f"Failed to copy {filename}. Reason: {e}")
            print(f"Failed to copy {filename}. Reason: {e}")
        
        progress_var.set((i + 1) / total_files * 100)
        root.update_idletasks()
    status_label.config(text=f"All macros copied you can now close this window. You need to run the indexer to index new macros and then open a pull request to contribute")
    print(f"All macros copied, You can now close this window. You need to run the indexer to index new macros and then open a pull request to contribute")

def start_copy():
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, padx=10, pady=10)
    
    status_label = tk.Label(root, text="Starting copy process...")
    print("Starting copy process...")
    status_label.pack(pady=10)
    
    copy_thread = threading.Thread(target=copy_files, args=(macros_path, output_path, progress_var, status_label))
    copy_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Macro Importer")
    
    start_button = tk.Button(root, text="Start Import", command=start_copy)
    start_button.pack(pady=20)
    
    root.mainloop()