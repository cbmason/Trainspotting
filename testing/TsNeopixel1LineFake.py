
import colors
import logging
from testing import sandbox
import traceback

logger = logging.getLogger(__name__)


class TsNeopixel1LineFake:
    """
    Notes:
        - Neopixel pitch is 0.277... inch / LED (20 inches 72 LEDs)
        - 23 total stops
        - One stop per LED would be 6.3"
    """
    NUM_PIXELS = 134
    DIRECTION_SOUTH = 0
    DIRECTION_NORTH = 1

    def __init__(self):
        self._last_updated_ts = 0
        self.CACHED_ID_TO_NAMES = {}
        self.CACHED_TRIP_TO_DIRECTION = {} # 0 = south, 1 = north
        self.CACHED_ID_TO_TRAVEL_TIME = {}
        self.CURRENT_PIXELS = {}
        self.FURTHEST_PER_TRAIN = {}
        self.led_model = ["" for _ in range(134)]
        self.led_model_trips = ["" for _ in range(134)]

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


    def _set_and_check_for_multiple(self, pixel_idx) -> int:
        if pixel_idx in self.CURRENT_PIXELS:
            self.CURRENT_PIXELS[pixel_idx] += 1
            return self.CURRENT_PIXELS[pixel_idx] - 1
        else:
            self.CURRENT_PIXELS[pixel_idx] = 1
            return 0

    def _set_pixel_stopped(self, pixel_idx: int, direction: int, trip_id: str):
        if self._set_and_check_for_multiple(pixel_idx) != 0:
            self.led_model[pixel_idx] = "WHITE"
        elif direction == self.DIRECTION_SOUTH:
            self.led_model[pixel_idx] = "LIGHT_RED"
        elif direction == self.DIRECTION_NORTH:
            self.led_model[pixel_idx] = "RED"
        else:
            self.led_model[pixel_idx] = "PURPLE"
        self.led_model_trips[pixel_idx] += trip_id

    def _set_pixel_moving(self, pixel_idx: int, direction: int, trip_id: str):
        if self._set_and_check_for_multiple(pixel_idx) != 0:
            self.led_model[pixel_idx] = "WHITE"
        if direction == self.DIRECTION_SOUTH:
            self.led_model[pixel_idx] = "LIGHT_GREEN"
        elif direction == self.DIRECTION_NORTH:
            self.led_model[pixel_idx] = "GREEN"
        else:
            self.led_model[pixel_idx] = "PINK"
        self.led_model_trips[pixel_idx] += trip_id

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
        for i in range(len(self.led_model)):
            self.led_model[i] = 0
            self.led_model_trips[i] = ""

    # body should be a Response.json object
    def update(self, body):
        self.clear_all_pixels()
        initialized = False
        current_furthest = {}
        self.CURRENT_PIXELS = {}
        self.CACHED_ID_TO_TRAVEL_TIME = {}

        # find all trains
        for train in body['data']['list']:
            if not initialized:
                try:
                    ref_dictionary_stops = body['data']['references']['stops']
                    self._populate_stop_map(ref_dictionary_stops)
                    ref_dictionary_trips = body['data']['references']['trips']
                    self._populate_trip_map(ref_dictionary_trips)
                    initialized = True

                except Exception as e:
                    logger.error(f"Unable to read reference dictionary: {e}")
                    return

            try:
                # for each, find where it is, and illuminate
                next_stop_id = train['status']['nextStop']
                distance_to_next = train['status']['nextStopTimeOffset']
                trip_id = train['tripId']

                # bail if we didn't find this in the global ref dict
                if next_stop_id not in self.CACHED_ID_TO_NAMES:
                    logger.warning(f"Couldn't find {next_stop_id} in stops, skipping...")
                    continue
                next_stop_name = self.CACHED_ID_TO_NAMES[next_stop_id]

                # bail if we didn't find this in the global ref dict
                if trip_id not in self.CACHED_TRIP_TO_DIRECTION:
                    logger.warning(f"Couldn't find {trip_id} in directions, skipping...")
                    continue
                direction = self.CACHED_TRIP_TO_DIRECTION[trip_id]

                # look at orientation to see which direction we're in
                if direction == self.DIRECTION_SOUTH:
                    idx_dict_to_use = self.STOP_IDX_DICT_SB
                elif direction == self.DIRECTION_NORTH:
                    idx_dict_to_use = self.STOP_IDX_DICT_NB
                else:
                    logger.warning(f"Direction {direction} unknown!")
                    idx_dict_to_use = self.STOP_IDX_DICT_NB

                # find position along stop:
                if distance_to_next == 0:
                    calculated_pixel = idx_dict_to_use[next_stop_name]
                else:
                    if next_stop_id not in self.CACHED_ID_TO_TRAVEL_TIME:
                        example_schedule = train['schedule']['stopTimes']
                        self._populate_stop_times(example_schedule)
                    distance_ratio = distance_to_next / self.CACHED_ID_TO_TRAVEL_TIME[next_stop_id]
                    if distance_ratio < 0.1:
                        calculated_pixel = idx_dict_to_use[next_stop_name]
                    elif distance_ratio < 0.6:
                        calculated_pixel = idx_dict_to_use[next_stop_name] - 1
                    else:
                        calculated_pixel = idx_dict_to_use[next_stop_name] - 2
                # The "FURTHEST_PER_TRAIN" table attempts to fix noisy and incorrect reporting by never going backwards.
                # We sanity check to make sure the train is close to where we think it is, if not then just take the
                # server's word for it no matter what.
                if trip_id in self.FURTHEST_PER_TRAIN:
                    if abs(self.FURTHEST_PER_TRAIN[trip_id] - calculated_pixel) < 3:
                        calculated_pixel = max(calculated_pixel, self.FURTHEST_PER_TRAIN[trip_id])
                if calculated_pixel in idx_dict_to_use.values() and distance_to_next == 0:
                    self._set_pixel_stopped(calculated_pixel, direction, trip_id)
                else:
                    self._set_pixel_moving(calculated_pixel, direction, trip_id)
                current_furthest[trip_id] = calculated_pixel

            except Exception as e:
                logger.error(f"Failed processing {train['tripId']}")
                logger.error(traceback.print_exc())
                continue

        self.FURTHEST_PER_TRAIN = current_furthest

    def print_names(self):
        num_rows = self.NUM_PIXELS // 2
        left = num_rows - 1 # due to 0 indexing
        right = num_rows
        for i in range(num_rows):
            print(f"[{self.led_model_trips[left - i]:<40}], [{self.led_model_trips[right + i]:>40}]")

    def print_colors(self):
        num_rows = self.NUM_PIXELS // 2
        left = num_rows - 1 # due to 0 indexing
        right = num_rows
        for i in range(num_rows):
            print(f"[{self.led_model[left - i]:<8}], [{self.led_model[right + i]:>8}]")


if __name__ == "__main__":
    server_packet = sandbox.query_server()
    testInstance = TsNeopixel1LineFake()
    testInstance.update(server_packet)
    testInstance.print_names()
    testInstance.print_colors()
