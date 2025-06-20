import logging
import os

from adafruit_blinka.microcontroller.amlogic.meson_g12_common.pin import board
from dotenv import load_dotenv

from StApiClient import StApiClient, StApiResponseHolder
from TsNeopixel import TsNeopixel
from TsNeopixel1Line import TsNeopixel1Line

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s]: %(message)s",
        handlers=[
            logging.FileHandler("trainspotting.log"),
            logging.StreamHandler()
        ]
    )


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

    def add_endpoint(self, route: str, response_holder: StApiResponseHolder):
        self.api_client.add_trips_for_route_query(route, response_holder)

    def add_line(self, line: TsNeopixel, response_holder: StApiResponseHolder):
        self.api_client.add_neopixel(line, response_holder)

    def update(self):
        self.api_client.update()


if __name__ == "__main__":
    setup_logging()
    # TODO: argparser
    # Instantiate program
    program = Trainspotting()

    # Create structures
    response1Line = StApiResponseHolder()
    neopixel1Line = TsNeopixel1Line(
        "1 Line",
        board.D18,
        response1Line
    )

    # Inject dependencies
    program.add_endpoint(StApiClient.ROUTE_1_LINE_ID, response1Line)
    program.add_line(neopixel1Line, response1Line)




