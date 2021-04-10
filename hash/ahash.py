import numpy as np
import cv2
from hash.hash import Hash
from numpy import int64

"""
" Implements average hash
"""


class AHash(Hash):

    def _calculate(self):
        g = type(self._img.pixel(0, 0)) == np.ndarray
        img = self._img
        if g:
            img = img.grayscale()

        img = img.resize((8, 8), cv2.INTER_AREA)
        averageValue = 0
        for row in range(8):
            for col in range(8):
                averageValue += img.pixel(col, row)

        averageValue /= 64
        result = int64()
        for row in range(8):
            for col in range(8):
                result <<= 1
                result |= 1 * (img.pixel(col, row) >= averageValue)

        return result

    def __eq__(self, h):
        return self.distanceTo(h) <= 10
