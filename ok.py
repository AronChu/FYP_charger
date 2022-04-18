if platform == 'android' or platform == 'ios':
    from plyer import gps

    gps.configure(on_location=self.update_blinker_position,
                  on_status=self.on_auth_status)
    gps.start(minTime=1000, minDistance=0)


def update_blinker_position(self, *args, **kwargs):
    my_lat = kwargs['lat']
    my_lon = kwargs['lon']
    my_lat = 30
    my_lon = 30
    print("GPS POSITION", my_lat, my_lon)
    gps_blinker = App.get_running_app().root.ids.mapview.ids.blinker
    gps_blinker.lat = my_lat
    gps_blinker.lon = my_lon


def on_auth_status(self, general_status, status_message):
    if general_status == 'provider-enabled':
        pass
    else:
        self.open_gps_access_popup()


def open_gps_access_popup(self):
    dialog = 