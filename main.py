import logging
import os
import time

#from adafruit_blinka.microcontroller.amlogic.meson_g12_common.pin import board
import board
from dotenv import load_dotenv

from StApiClient import StApiClient
from StApiResponseHolder import StApiResponseHolder
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
    def __init__(
            self,
            api_key: str
    ):
        # set up interface
        if api_key == "none":
            raise EnvironmentError("No API key provided.")
        self.api_client = StApiClient(api_key)

    def add_endpoint(self, route: str, response_holder: StApiResponseHolder):
        self.api_client.add_trips_for_route_query(route, response_holder)

    def add_line(self, line: TsNeopixel, response_holder: StApiResponseHolder):
        self.api_client.add_neopixel(line, response_holder)

    def update(self):
        self.api_client.update()


if __name__ == "__main__":
    setup_logging()
    load_dotenv()

    env_sample_period_sec = int(os.getenv("TRAIN_PERIOD_SEC", 6))
    env_sample_period_sec = min(60, max(env_sample_period_sec, 5))  # limit update period to [5, 60] seconds
    env_api_key = os.getenv("OBA_API_KEY", "none")

    program = Trainspotting(env_api_key)

    # Create structures
    response1Line = StApiResponseHolder()
    neopixel1Line = TsNeopixel1Line(
        "1 Line",
        board.D18,
        response1Line,
        brightness=0.10,
        byteorder="GRB"
    )

    # Inject dependencies
    program.add_endpoint(StApiClient.ROUTE_1_LINE_ID, response1Line)
    program.add_line(neopixel1Line, response1Line)

    try:
        # Run forever
        while True:
            program.update()
            time.sleep(env_sample_period_sec)
    finally:
        neopixel1Line.clear_all_pixels()
