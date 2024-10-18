from abc import ABC, abstractmethod

import requests


class AbstractAdsbClient(ABC):

    @abstractmethod
    def get(self):
        pass


class AdsbClient(AbstractAdsbClient):

    def get(self):
        URL = "http://localhost:8080/data.json"
        return requests.get(url=URL)
