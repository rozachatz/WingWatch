import requests


class AdsbClient:

    def getAdsb(self):
        URL = "http://localhost:8080/data.json"
        return requests.get(url=URL)
