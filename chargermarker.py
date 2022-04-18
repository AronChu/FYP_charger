from kivy_garden.mapview import MapMarkerPopup
from locationpopupmenu import LocationPopupMenu


class ChargerMarker(MapMarkerPopup):
    charger_data = []
    def on_release(self):
        menu = LocationPopupMenu(self.charger_data)
        menu.size_hint = [.8,.9]
        menu.open()