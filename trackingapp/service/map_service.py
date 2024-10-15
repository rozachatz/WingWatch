import webbrowser

import folium


class MapService:

    def __init__(self) -> None:
        self.map_object = folium.Map(location=[38.0, 23.0], zoom_control=True, control_scale=True)
        self.map_object.save("map.html")
        webbrowser.open("map.html")

    def create_map(self, coordinates):
        for coord in coordinates:
            folium.Marker(location=[coord['lat'], coord['lon']]).add_to(self.map_object)
            self.map_object.save("map.html")  # TODO: Dynamic map
