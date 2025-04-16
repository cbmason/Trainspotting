import os

from dotenv import load_dotenv

from StApiClient import StApiClient, StApiResponseHolder
from TsNeopixel import TsNeopixel


class Trainspotting:
    def __init__(self):
        # set up interface
        # register all lines
        load_dotenv()

        self.sample_period_sec = os.getenv("TRAIN_PERIOD_SEC", 10)
        self.sample_period_sec = min(60, max(self.sample_period_sec, 5)) # limit update period to [5, 60] seconds
        self.api_key = os.getenv("OBA_API_KEY", "none")
        if self.api_key == "none":
            raise EnvironmentError("No API key provided.")
        self.api_client = StApiClient(self.api_key)
        self.lines = []

    def add_endpoint(self, route: str, response_holder: StApiResponseHolder):
        self.api_client.add_trips_for_route_query(route, response_holder)

    def add_line(self, line: TsNeopixel):
        self.lines.append(line)

    def update(self):
        # ping the API for each line
        # set the pixels for each line
        pass



