import os

from dotenv import find_dotenv, load_dotenv


class Settings:
    def __init__(self):
        env_file = find_dotenv(f'.env.{os.getenv("ENV", "secrets")}')
        load_dotenv(env_file)
        self.latitude = float(os.getenv("LATITUDE"))
        self.longitude = float(os.getenv("LONGITUDE"))
        self.altitude = float(os.getenv("ALTITUDE"))

settings = Settings()