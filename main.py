from kivymd.app import MDApp
from homemapview import HomeMapView
from kivy_garden import mapview
from searchpopupmenu import SearchPopupMenu
from kivy.core.window import Window
from gpshelper import GpsHelper
import sqlite3
class MainApp(MDApp):
    connection = None
    cursor = None
    search_menu = None
    Window.size = (400, 775)
    def on_start(self):
        GpsHelper().run()
        self.connection = sqlite3.connect("COORDINATE.db")
        self.cursor = self.connection.cursor()
        self.search_menu = SearchPopupMenu()
MainApp().run()