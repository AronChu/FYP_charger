from kivy_garden.mapview import MapView, MapSource, MapMarker, MapMarkerPopup
from kivy.clock import Clock
from kivy.app import App
from kivy_garden.mapview import MapMarkerPopup
from chargermarker import ChargerMarker

class HomeMapView(MapView):
    charger_locations = []
    getting_chargers_timer = None

    def start_getting_chargers_in_fov(self):
        try:
            self.getting_chargers_timer.cancel()
        except:
            pass

        self.getting_chargers_timer = Clock.schedule_once(self.get_chargers_in_fov,1)

    def get_chargers_in_fov(self, *args):
        app = App.get_running_app()
        sql_statement = "SELECT * from coordinates"
        app.cursor.execute(sql_statement)
        chargers = app.cursor.fetchall()
        for charger in chargers:
            location = charger[2]
            self.add_charger(charger)

    def add_charger(self, charger):
        lat = charger[0]
        lon = charger[1]
        marker = ChargerMarker(lat = lat, lon = lon,source = 'EVCEI.png')
        marker.charger_data = charger
        self.add_widget(marker)
        location = charger[2]
        self.charger_locations.append(location)
