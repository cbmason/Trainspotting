from abc import ABC

from TsNeopixel import TsNeopixel


class TsNeopixel1Line(TsNeopixel):
    """
    Notes:
        - Neopixel pitch is 0.277... inch / LED (20 inches 72 LEDs)
        - 23 total stops
        - One stop per LED would be 6.3"

    """
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

    def _determine_lit_pixel(self):
        pass