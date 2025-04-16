import logging
import requests
import validators

class StApiResponseHolder:
    def __init__(self):
        self.response = None
        # self.stale = False TODO: do we want this?

class StApiClient:
    AGENCY_ST_ID = "40"
    ROUTE_1_LINE_ID = "40_100479"
    ROUTE_2_LINE_ID = "40_2LINE"
    BASE_URL = "https://api.pugetsound.onebusaway.org/api/where"

    def __init__(self, api_key: str):
        self.endpoints = {}
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

    def update(self):
        params = {'key': self.api_key}
        for endpoint, container in self.endpoints.items():
            response = requests.get(endpoint, params=params)
            if response.status_code != 200:
                logging.ERROR(f"{endpoint} returned code {response.status_code}")
            container.response = response.text



    # closest station and displacement are how this works
    # maybe have a LED in between stations?
