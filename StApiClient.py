import logging
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests
import validators

from StApiResponseHolder import StApiResponseHolder
from TsNeopixel import TsNeopixel


logger = logging.getLogger(__name__)

class StApiClient:
    AGENCY_ST_ID = "40"
    ROUTE_1_LINE_ID = "40_100479"
    ROUTE_2_LINE_ID = "40_2LINE"
    BASE_URL = "https://api.pugetsound.onebusaway.org/api/where"

    def __init__(self, api_key: str):
        self.endpoints = {}
        self.neopixels = {}
        self.api_key = api_key

    def add_trips_for_route_query(self, route: str, response_holder: StApiResponseHolder):
        """
        Add a route to query using Trips For Route
        :param route: The route to add
        :param response_holder: A StApiResponseHolder object that this client will populate with the latest response
            every update()
        :return: None
        """
        endpoint = f"/trips-for-route/{route}.json"
        new_url = self.BASE_URL + endpoint
        if not validators.url(new_url):
            raise ValueError("Invalid route")
        self.endpoints[new_url] = response_holder

    def add_neopixel(self, neopixel: TsNeopixel, response_holder: StApiResponseHolder):
        self.neopixels[neopixel] = response_holder

    def update(self):
        params = {'key': self.api_key}
        for endpoint, container in self.endpoints.items():
            response = requests.get(endpoint, params=params)
            if response is None:
                logger.error(f"Server did not respond!")
                return 0
            if response.status_code != 200:
                logger.error(f"{endpoint} returned code {response.status_code}")
                if response.status_code == 429:
                    try:
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            # Try interpreting it as seconds
                            wait_seconds = int(retry_after)
                            logger.error(f"Server says to retry after {wait_seconds} seconds.")
                            return wait_seconds
                        else: # assume a 60 second backoff
                            logger.error(f"Could not find 'Retry-After' header.  Retrying in 60s")
                            return 60
                    except ValueError:
                        # If not an integer, try parsing it as a date
                        # TODO
                        logger.error(f"Server says to retry after certain date, TODO: need to handle this")
                        return 0

            container.set_response(response)
        wait_seconds = 0
        for line in self.neopixels.keys():
            wait_seconds = line.update()
            if wait_seconds != 0:
                return wait_seconds
        return 0


    # closest station and displacement are how this works
    # maybe have a LED in between stations?
