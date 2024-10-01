import folium
import webbrowser
from app.dao.AdsbClient import AdsbClient

class MapService:

    def __init__(self, api_client: AdsbClient) -> None:
        self.api_client = api_client
        self.map_object = folium.Map(location=[37.0, 13.0], zoom_control=True, control_scale=True)
        self.map_object.save("map.html")
        webbrowser.open("map.html")


    def create_map(self):
        data = self.api_client.getAdsb()

        # iterate dictionary
        for aircraft in data:
            #altitude = aircraft.get('altitude')
            #flight = aircraft.get('flight').strip()
            #hex_code = aircraft.get('hex')
            #speed = aircraft.get('speed')
            #track = aircraft.get('track')
            latitude = aircraft.get('lat')
            longitude = aircraft.get('lon')

            folium.Marker(location=[latitude,longitude ]).add_to(self.map_object)
            self.map_object.save("map.html") # you have to refresh to see the route.
            # TODO: Dynamic map






