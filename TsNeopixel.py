from abc import abstractmethod, ABC

import board
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

from StApiClient import StApiResponseHolder


class TsNeopixel(adafruit_pixelbuf.PixelBuf, ABC):
    def __init__(
            self,
            name: str,
            pin: board.pin,
            size: int,
            response_holder: StApiResponseHolder,
            **kwargs):
        self._name = name
        self._pin = pin
        self.response_holder = response_holder
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

    @abstractmethod
    def update(self):
        raise NotImplementedError("Must be subclassed")

    def __hash__(self):
        return hash(self._name)

