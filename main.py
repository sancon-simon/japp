from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
import os
from datetime import datetime
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.image import Image
from kivymd.uix.card import MDCard  
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle

class MainApp(MDApp):
    def build(self):
        Window.size = (375, 667)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "500"

        self.store = JsonStore('file_store.json')

        # Load the KV file
        self.manager = Builder.load_file("main.kv")
        self.recent_images = []  # List to store recent image paths

        # Load the last path if available
        last_path = ''
        if self.store.exists('last_path'):
            last_path = self.store.get('last_path')['path']
        self.load_last_path(last_path)

        return self.manager

    def file_manager_open(self):
        if self.store.exists('last_dir'):
            last_dir = self.store.get('last_dir')['path']
        else:
            last_dir = os.path.expanduser("~")

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            preview=True,
            select_path=self.select_path,
            ext=['.png', '.jpg', '.jpeg']  # specify the file extensions you want to allow
        )
        self.file_manager.show(last_dir)

    def select_path(self, path):
        '''
        This function will be called when a file is selected.
        '''
        self.exit_manager()
        MDSnackbar(
            MDSnackbarText(
                text=path,
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()

        self.store.put('last_path', path=path)
        self.store.put('last_dir', path=os.path.dirname(path))
        self.load_last_path(path)

        self.add_to_recent_images(path)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''
        self.manager_open = False
        self.file_manager.close()

    def toggle_theme_style(self, is_active):
        self.theme_cls.theme_style = "Dark" if is_active else "Light"

    def load_last_path(self, path):
        '''
        This function will be called to load the last selected path.
        '''
        selected_image = self.manager.get_screen('upload').ids.selected_image
        selected_image.source = path

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def menu_open(self):
        menu_items = [
            {
                "text": "Settings",
                "on_release": lambda x="Settings": self.menu_callback(x),
            },
            {
                "text": "About Us",
                "on_release": lambda x="About Us": self.menu_callback(x),
            }

        ]
        self.menu = MDDropdownMenu(
            caller=self.manager.get_screen('main').ids.button_menu, items=menu_items
        )
        self.menu.open()

    def add_to_recent_images(self, path):
        '''
        Add the selected image path to the list of recent images and update the UI.
        '''
        date_taken = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if path not in self.recent_images:
            self.recent_images.append((path, date_taken))
            if len(self.recent_images) > 5:  # Keep only the last 5 images
                self.recent_images.pop(0)
            self.update_recent_images()

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_recent_images(self):
        '''
        Update the recent images screen with the current list of recent images.
        '''
        recent_screen = self.manager.get_screen('recent')
        recent_layout = recent_screen.ids.recent_images_layout
        recent_layout.clear_widgets()  # Clear the layout before adding new images

        for image_path, date_taken in self.recent_images:
            card = MDCard(
                orientation='vertical',
                size_hint=(None, None),
                size=(dp(220), dp(200)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )

            img = Image(source=image_path, size_hint_y=.7, pos_hint={"top": 1}, allow_stretch=True, keep_ratio=False)
            label = MDLabel(text=date_taken, size_hint_y=None, height=dp(30), halign='center')

            # Add widgets to the card
            card.add_widget(img)
            card.add_widget(label)
            recent_layout.add_widget(card)


    def menu_callback(self, text_item):
        if text_item == "Settings":
            self.switch_screen('settings')
        elif text_item == "About Us":
            self.switch_screen('about')
        self.menu.dismiss()

    def switch_screen(self, screen_name):
        self.manager.current = screen_name

    def open_theme_picker(self):
        theme_dialog = MDThemePicker()
        theme_dialog.open()

class ScreenMain(Screen):
    pass

class ScreenInstruction(Screen):
    pass

class ScreenRecent(Screen):
    pass

class ScreenAbout(Screen):
    pass

class ScreenSettings(Screen):
    pass

class ScreenUpload(Screen):
    pass

class ScreenConsole(Screen):
    pass

class WindowManager(ScreenManager):
    pass

if __name__ == '__main__':
    MainApp().run()
