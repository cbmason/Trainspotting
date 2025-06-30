import time
import requests

class StApiResponseHolder:
    def __init__(self):
        self._response = None
        self._timestamp = 0

    def set_response(self, response):
        self._response = response
        self._timestamp = time.time()

    def get_response(self) -> requests.Response:
        return self._response

    def get_timestamp(self):
        return self._timestamp

