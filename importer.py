import os
import shutil

macros_path = os.path.join(os.getenv('LOCALAPPDATA'), "GeometryDash", "geode", "mods", "tobyadd.gdh", "Macros")
output_path = os.path.join(".", "Macros")

def copy_files(folder_path, output_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            shutil.copy(file_path, output_path)
            print(f"Copied {filename} successfully.")
        except Exception as e:
            print(f"Failed to copy {filename}. Reason: {e}")

copy_files(macros_path, output_path)
