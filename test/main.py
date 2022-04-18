from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.bubble import Bubble, BubbleButton
from kivy_garden.mapview import MapView, MapSource, MapMarker, MapMarkerPopup
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from plyer import gps
import csv

class chargers():
    file = open('coordinate.csv')
    csv_reader = csv.reader(file)
    next(csv_reader)
    lat = []
    lon = []
    coordinate = []
    address = []
    for row in csv_reader:
        coordinate.append(row)
    for charger in coordinate:
        lat.append(float(charger[0]))
        lon.append(float(charger[1]))
        address.append(charger[2])

chargers = chargers()
Window.size = (375, 675)


class main(App):
    def build(self):
        float_layout = FloatLayout()
        map_view = MapView()
        float_layout.add_widget(map_view)
        i = 0
        while(i<len(chargers.lat)):
            bubble = Bubble()
            bubble.size_hint = (2.5,2)
            bubble.show_arrow = 0
            button = BubbleButton(text = chargers.address[i])
            bubble.add_widget(button)
            map_marker = MapMarkerPopup()
            map_marker.lat = chargers.lat[i]
            map_marker.lon = chargers.lon[i]
            map_marker.source = "EVCEI.png"
            map_marker.add_widget(bubble)
            map_view.add_widget(map_marker)
            i += 1
        return float_layout

main().run()
