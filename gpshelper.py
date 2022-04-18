from kivy.app import App
from kivy.utils import platform

class GpsHelper():
    def run(self):
        gps_blinker = App.get_running_app().root.ids.mapview.ids.blinker
        gps_blinker.blink()

