import requests

class AdsbClient:

    def getAdsb(self):
        URL = "http://localhost:8080/data.json"
        r = requests.get(url = URL)
        return r.json()




