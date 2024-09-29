import os
import json
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
import darkdetect  # Import darkdetect
from urllib.parse import quote

def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    size_gb = size_mb / 1024
    
    if size_gb >= 1:
        return f"{size_gb:.2f} GB"
    elif size_mb >= 1:
        return f"{size_mb:.2f} MB"
    elif size_kb >= 1:
        return f"{size_kb:.2f} KB"
    else:
        return f"{size_bytes} bytes"

def create_index_entry(file_path, tags, no_noclip_used, creator, link):
    file_name = os.path.basename(file_path)
    file_name_without_extension = os.path.splitext(file_name)[0]
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    size = get_file_size(file_path)
    
    return {
        "name": file_name_without_extension,
        "tags": tags,
        "no noclip used": no_noclip_used,
        "creator": creator,
        "date": date,
        "size": size,
        "link": link
    }

class IndexerApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark" if darkdetect.theme() == "Dark" else "Light"
        self.indexes = []
        self.load_indexes()
        self.files = [f for f in os.listdir("./Macros") if os.path.isfile(os.path.join("./Macros", f))]
        self.current_file_index = 0
        self.dialog = None
        return self.create_ui()

    def load_indexes(self):
        indexes_file = "./indexes.json"
        if os.path.exists(indexes_file):
            try:
                with open(indexes_file, 'r') as f:
                    self.indexes = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {indexes_file} contains invalid JSON. Initializing with an empty list.")

    def create_ui(self):
        layout = BoxLayout(orientation='vertical')
        self.label = Label(text=f"Processing file: {self.files[self.current_file_index]}")
        layout.add_widget(self.label)
        self.next_button = MDRaisedButton(text="Next", on_release=self.next_file)
        layout.add_widget(self.next_button)
        return layout

    def next_file(self, instance):
        file_name = self.files[self.current_file_index]
        file_path = os.path.join("./Macros", file_name)
        file_name_without_extension = os.path.splitext(file_name)[0]
        
        if any(entry["name"] == file_name_without_extension for entry in self.indexes):
            self.show_overwrite_dialog(file_path)
        else:
            self.show_input_dialog(file_path)

    def show_overwrite_dialog(self, file_path):
        content = BoxLayout(orientation='vertical', size_hint_y=None, height=100)
        content.add_widget(Label(text=f"File {os.path.basename(file_path)} already exists in indexes."))
        
        self.overwrite_dialog = MDDialog(
            title="File Exists",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Overwrite", on_release=lambda x: self.overwrite_file(file_path)),
                MDRaisedButton(text="Skip", on_release=lambda x: self.skip_file())
            ],
            size_hint=(None, None),
            size=(400, 200)
        )
        self.overwrite_dialog.open()

    def overwrite_file(self, file_path):
        self.overwrite_dialog.dismiss()
        self.show_input_dialog(file_path)

    def skip_file(self):
        self.overwrite_dialog.dismiss()
        self.current_file_index += 1
        if self.current_file_index < len(self.files):
            self.label.text = f"Processing file: {self.files[self.current_file_index]}"
        else:
            self.save_indexes()
            self.stop()

    def show_input_dialog(self, file_path):
        content = BoxLayout(orientation='vertical', size_hint_y=None, height=300)  # Set a fixed height for the content
        tags_input = MDTextField(hint_text="Enter tags separated by spaces")
        no_noclip_used_checkbox = MDCheckbox(active=False, size_hint=(None, None), size=(48, 48))
        creator_input = MDTextField(hint_text="Enter creator")
        
        content.add_widget(tags_input)
        content.add_widget(Label(text="No noclip used:"))
        content.add_widget(no_noclip_used_checkbox)
        content.add_widget(creator_input)
        
        self.dialog = MDDialog(
            title=f"Input for {os.path.basename(file_path)}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Submit", on_release=lambda x: self.submit_input(file_path, tags_input.text, no_noclip_used_checkbox.active, creator_input.text))
            ],
            size_hint=(None, None),  # Disable automatic size hinting
            size=(400, 400)  # Set a fixed size for the dialog
        )
        self.dialog.open()

    def submit_input(self, file_path, tags, no_noclip_used, creator):
        file_name = os.path.basename(file_path)
        encoded_file_name = quote(file_name)
        link = f"https://github.com/LousyBook-01/ReplayEngine-Macros-GD/raw/refs/heads/master/Macros/{encoded_file_name}"
        entry = create_index_entry(file_path, tags.split(), no_noclip_used, creator, link)
        
        # Remove the old entry with the same name
        file_name_without_extension = os.path.splitext(file_name)[0]
        self.indexes = [entry for entry in self.indexes if entry["name"] != file_name_without_extension]
        
        self.indexes.append(entry)
        
        self.dialog.dismiss()
        self.current_file_index += 1
        if self.current_file_index < len(self.files):
            self.label.text = f"Processing file: {self.files[self.current_file_index]}"
        else:
            self.save_indexes()
            self.stop()

    def save_indexes(self):
        with open("./indexes.json", 'w') as f:
            json.dump(self.indexes, f, indent=4)
        print("Indexes saved to indexes.json")

if __name__ == "__main__":
    IndexerApp().run()