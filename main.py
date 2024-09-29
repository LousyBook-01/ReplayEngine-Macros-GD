import os
import json
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.selectioncontrol import MDCheckbox
import darkdetect  # Import darkdetect

class DownloaderApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark" if darkdetect.theme() == "Dark" else "Light"
        self.indexes_url = "https://github.com/LousyBook-01/ReplayEngine-Macros-GD/raw/refs/heads/master/indexes.json"
        self.cache_dir = "./cache"
        self.cache_file = os.path.join(self.cache_dir, "indexes.json")
        self.download_dir = os.path.join("C:\\Users\\LousyBook\\AppData\\Local\\GeometryDash\\geode\\mods\\tobyadd.gdh\\Macros")
        self.indexes = []
        self.load_indexes()
        return self.create_ui()

    def load_indexes(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.indexes = json.load(f)
        else:
            self.download_indexes()

    def download_indexes(self):
        try:
            response = requests.get(self.indexes_url)
            if response.status_code == 200:
                self.indexes = response.json()
                with open(self.cache_file, 'w') as f:
                    json.dump(self.indexes, f, indent=4)
            else:
                print("Failed to download indexes.json")
        except requests.exceptions.RequestException:
            print("No internet connection. Using cached indexes if available.")

    def create_ui(self):
        layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Downloaded Macros")
        layout.add_widget(self.label)
        
        self.scroll_view = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll_view.add_widget(self.list_layout)
        layout.add_widget(self.scroll_view)
        
        self.refresh_button = MDRaisedButton(text="Refresh", on_release=self.refresh_list)
        layout.add_widget(self.refresh_button)
        
        self.refresh_list(None)
        return layout

    def refresh_list(self, instance):
        self.list_layout.clear_widgets()
        for entry in self.indexes:
            item = TwoLineAvatarIconListItem(
                text=entry["name"],
                secondary_text=f"Creator: {entry['creator']}, Size: {entry['size']}"
            )
            download_button = IconRightWidget(icon="download", on_release=lambda x, link=entry["link"], name=entry["name"]: self.download_macro(link, name))
            delete_button = IconRightWidget(icon="delete", on_release=lambda x, name=entry["name"]: self.delete_macro(name))
            item.add_widget(download_button)
            item.add_widget(delete_button)
            self.list_layout.add_widget(item)

    def download_macro(self, link, name):
        if not self.check_internet_connection():
            self.show_message("Connect to the internet to download macros.")
            return
        
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
        file_path = os.path.join(self.download_dir, name + ".re")
        if os.path.exists(file_path):
            self.show_message(f"{name} already exists.")
            return
        
        response = requests.get(link)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            self.show_message(f"{name} downloaded successfully.")
        else:
            self.show_message(f"Failed to download {name}.")

    def delete_macro(self, name):
        file_path = os.path.join(self.download_dir, name + ".re")
        if os.path.exists(file_path):
            os.remove(file_path)
            self.show_message(f"{name} deleted successfully.")
        else:
            self.show_message(f"{name} does not exist.")

    def check_internet_connection(self):
        try:
            requests.get("http://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def show_message(self, message):
        self.dialog = MDDialog(
            title="Message",
            text=message,
            buttons=[
                MDRaisedButton(text="OK", on_release=lambda x: self.dialog.dismiss())
            ],
        )
        self.dialog.open()

if __name__ == "__main__":
    DownloaderApp().run()