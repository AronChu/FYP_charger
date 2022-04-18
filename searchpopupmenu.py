from kivymd.uix.dialog import MDInputDialog
from urllib import parse
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
class SearchPopupMenu(MDInputDialog):
    title = 'Search by Address'
    text_button_ok = "Search"
    def __init__(self):
        super().__init__()
        self.size_hint = [.9,.3]
        self.events_callback = self.callback

    def callback(self,*args):
        address = self.text_field.text
        self.geocode_get_lat_lon(address)

    def geocode_get_lat_lon(self, address):
        address = parse.quote(address)
        url = "https://geocode.search.hereapi.com/v1/geocode?q=%s&apiKey=QksctopKJ0jJfyr-I3o7oXYRViKwrcubu04r9ryGupg"%(address)
        UrlRequest(url, on_success = self.success, on_failure= self.failure, on_error= self.error)

    def success(self,urlrequest, result):
        print("Success")
        latitude = result['items'][0]['position']['lat']
        longitude = result['items'][0]['position']['lng']
        print(latitude,longitude)
        app = App.get_running_app()
        mapview = app.root.ids.mapview
        mapview.center_on(latitude,longitude)

    def error(self, urlrequest, result):
        print("Error")
        print(result)
    def failure(self, urlrequest, result):
        print("Failure")
        print(result)