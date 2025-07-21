from abc import ABC

import adafruit_pixelbuf
import board
import logging

import colors
from StApiClient import StApiResponseHolder
from TsNeopixel import TsNeopixel

logger = logging.getLogger(__name__)

class TsNeopixel1Line(TsNeopixel):
    """
    Notes:
        - Neopixel pitch is 0.277... inch / LED (20 inches 72 LEDs)
        - 23 total stops
        - One stop per LED would be 6.3"
    """
    NUM_PIXELS = 134
    DIRECTION_SOUTH = 0
    DIRECTION_NORTH = 1

    def __init__(
            self,
            name: str,
            pin: board.pin,
            response_holder: StApiResponseHolder,
            brightness: float,
            **kwargs):
        super().__init__(name, pin, self.NUM_PIXELS, response_holder, brightness=brightness, **kwargs)
        self._last_updated_ts = 0

    STOP_IDX_DICT_NB = {
        "Angle Lake": 0,
        "SeaTac/Airport": 3,
        "Tukwila Int'l Blvd": 6,
        "Rainier Beach": 9,
        "Othello": 12,
        "Columbia City": 15,
        "Mount Baker": 18,
        "Beacon Hill": 21,
        "SODO": 24,
        "Stadium": 27,
        "Int'l Dist/Chinatown": 30,
        "Pioneer Square": 33,
        "Symphony": 36,
        "Westlake": 39,
        "Capitol Hill": 42,
        "Univ of Washington": 45,
        "U District": 48,
        "Roosevelt": 51,
        "Northgate": 54,
        "Shoreline South/148th": 57,
        "Shoreline North/185th": 60,
        "Mountlake Terrace": 63,
        "Lynnwood City Center": 66
    }

    STOP_IDX_DICT_SB = {
        "Angle Lake": 133,
        "SeaTac/Airport": 130,
        "Tukwila Int'l Blvd": 127,
        "Rainier Beach": 124,
        "Othello": 121,
        "Columbia City": 118,
        "Mount Baker": 115,
        "Beacon Hill": 112,
        "SODO": 109,
        "Stadium": 106,
        "Int'l Dist/Chinatown": 103,
        "Pioneer Square": 100,
        "Symphony": 97,
        "Westlake": 94,
        "Capitol Hill": 91,
        "Univ of Washington": 88,
        "U District": 85,
        "Roosevelt": 82,
        "Northgate": 79,
        "Shoreline South/148th": 76,
        "Shoreline North/185th": 73,
        "Mountlake Terrace": 70,
        "Lynnwood City Center": 67,
    }

    CACHED_ID_TO_NAMES = {}
    CACHED_TRIP_TO_DIRECTION = {} # 0 = south, 1 = north
    CACHED_ID_TO_TRAVEL_TIME = {}

    def _set_pixel_stopped(self, pixel_idx: int, direction: int):
        # logger.info(f"setting {pixel_idx}")
        if direction == self.DIRECTION_SOUTH:
            self[pixel_idx] = colors.colors["LIGHT_RED"]
        else:
            self[pixel_idx] = colors.colors["RED"]

    def _set_pixel_moving(self, pixel_idx: int, direction: int):
        # logger.info(f"setting {pixel_idx}")
        if direction == self.DIRECTION_SOUTH:
            self[pixel_idx] = colors.colors["LIGHT_GREEN"]
        else:
            self[pixel_idx] = colors.colors["GREEN"]

    def _populate_stop_map(self, ref_dictionary_stops: dict):
        self.CACHED_ID_TO_NAMES = {}
        for stop in ref_dictionary_stops:
            self.CACHED_ID_TO_NAMES[stop['id']] = stop['name']

    def _populate_trip_map(self, ref_dictionary_trips: dict):
        self.CACHED_TRIP_TO_DIRECTION = {}
        for trip in ref_dictionary_trips:
            self.CACHED_TRIP_TO_DIRECTION[trip['id']] = int(trip['directionId'])

    def _populate_stop_times(self, train_schedule: dict):
        # The zeroth stop is the beginning of the run, so shouldn't have "travel time", instead use the boarding time
        self.CACHED_ID_TO_TRAVEL_TIME[train_schedule[0]['stopId']] = (
            train_schedule[0]['departureTime'] - train_schedule[0]['arrivalTime']
        )
        if self.CACHED_ID_TO_TRAVEL_TIME[train_schedule[0]['stopId']] == 0: # defend against div by zero
            self.CACHED_ID_TO_TRAVEL_TIME[train_schedule[0]['stopId']] = 1
        for stop_idx in range(1, len(train_schedule)):
            self.CACHED_ID_TO_TRAVEL_TIME[train_schedule[stop_idx]['stopId']] = (
                    train_schedule[stop_idx]['arrivalTime'] -
                    train_schedule[stop_idx - 1]['arrivalTime'])
            if self.CACHED_ID_TO_TRAVEL_TIME[train_schedule[stop_idx]['stopId']] == 0:  # defend against div by zero
                self.CACHED_ID_TO_TRAVEL_TIME[train_schedule[stop_idx]['stopId']] = 1

    def clear_all_pixels(self):
        self.fill(0)
        self.show()

    def update(self):
        # check timestamp to make sure we haven't already processed this
        if self.response_holder.get_timestamp() == self._last_updated_ts:
            return
        self._last_updated_ts = self.response_holder.get_timestamp()

        # verify validity
        server_response = self.response_holder.get_response()
        if server_response.status_code != 200:
            logger.error(f"Error: Server responded with {server_response.status_code}")
            return
        body = server_response.json()

        self.clear_all_pixels()

        # find all trains
        for train in body['data']['list']:
            try:
                # for each, find where it is, and illuminate
                next_stop_id = train['status']['nextStop']
                distance_to_next = train['status']['nextStopTimeOffset']
                trip_id = train['tripId']

                # cross reference the ID to [references][stops], which will have the name.  Check the cache first
                if next_stop_id not in self.CACHED_ID_TO_NAMES:
                    ref_dictionary_stops = body['data']['references']['stops']
                    # See if this stop in the refdict, if so: repopulate the cache, if not, we can't do anything
                    if any(item['id'] == next_stop_id for item in ref_dictionary_stops):
                        self._populate_stop_map(ref_dictionary_stops)
                    else:
                        continue
                next_stop_name = self.CACHED_ID_TO_NAMES[next_stop_id]

                # cross reference the trip ID to [references][trips], which will have the direction
                if trip_id not in self.CACHED_TRIP_TO_DIRECTION:
                    ref_dictionary_trips = body['data']['references']['trips']
                    # See if this stop in the refdict, if so: repopulate the cache, if not, we can't do anything
                    if any(item['id'] == trip_id for item in ref_dictionary_trips):
                        self._populate_trip_map(ref_dictionary_trips)
                    else:
                        continue
                direction = self.CACHED_TRIP_TO_DIRECTION[trip_id]

                # look at orientation to see which direction we're in
                if direction == self.DIRECTION_SOUTH:
                    idx_dict_to_use = self.STOP_IDX_DICT_SB
                else:
                    idx_dict_to_use = self.STOP_IDX_DICT_NB

                # find position along stop:
                if distance_to_next == 0:
                    self._set_pixel_stopped(idx_dict_to_use[next_stop_name], direction)
                else:
                    if next_stop_id not in self.CACHED_ID_TO_TRAVEL_TIME:
                        example_schedule = train['schedule']['stopTimes']
                        self._populate_stop_times(example_schedule)
                    distance_ratio = distance_to_next / self.CACHED_ID_TO_TRAVEL_TIME[next_stop_id]
                    if distance_ratio < 0.01:
                        self._set_pixel_moving(idx_dict_to_use[next_stop_name], direction)
                    elif distance_ratio < 0.5:
                        self._set_pixel_moving(idx_dict_to_use[next_stop_name] - 1, direction)
                    else:
                        self._set_pixel_moving(idx_dict_to_use[next_stop_name] - 2, direction)
            except Exception as e:
                logger.error(f"Failed processing {train['tripId']}: {e}")

        self.show()
