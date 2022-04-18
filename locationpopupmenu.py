from kivymd.uix.dialog import ListMDDialog

class LocationPopupMenu(ListMDDialog):
    def __init__(self, chargers_data):
        super().__init__()
        self.foo = 'bar'
        headers = "location,StandardBS1363,MediumIEC62196,MediumSAEJ1772,MediumOthers,QuickCHAdeMO,QuickCCSDCCombo,QuickIEC62196,QuickGBT,QuickOthers,RemarkOthers"
        headers = headers.split(',')
        for i in range (len(headers)):
            attribute_location = headers[i]
            attribute_value = chargers_data[i+2]
            setattr(self, attribute_location, attribute_value)
