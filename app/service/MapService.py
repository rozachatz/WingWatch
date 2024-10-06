import folium
import webbrowser
from app.dao.AdsbClient import AdsbClient

class MapService:

    def __init__(self) -> None:
        self.map_object = folium.Map(location=[38.0, 23.0], zoom_control=True, control_scale=True)
        self.map_object.save("map.html")
        webbrowser.open("map.html")


    def create_map(self, data):
        #altitude = data.get('altitude')
        latitude = data.get('lat')
        longitude = data.get('lon')

        folium.Marker(location=[latitude,longitude ]).add_to(self.map_object)
        self.map_object.save("map.html") # you have to refresh to see the route.
        # TODO: Dynamic map






