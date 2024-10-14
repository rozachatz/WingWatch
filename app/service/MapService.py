import webbrowser

import folium


class MapService:

    def __init__(self) -> None:
        self.map_object = folium.Map(location=[38.0, 23.0], zoom_control=True, control_scale=True)
        self.map_object.save("map.html")
        webbrowser.open("map.html")

    def create_map(self, data):
        if isinstance(data, list):
            for entry in data:
                folium.Marker(location=[entry['lat'], entry['lon']]).add_to(self.map_object)
                self.map_object.save("map.html")  # TODO: Dynamic map
