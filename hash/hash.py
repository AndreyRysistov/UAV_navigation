class Hash(object):
    _img = False
    _value = False

    def __init__(self, img):
        self._img = img
        self._value = self._calculate()

    def _calculate(self):
        raise NotImplementedError

    @property
    def value(self):
        return self._value

    @property
    def img(self):
        return self._img

    def __str__(self):
        return str(abs(self._value))

    @staticmethod
    def hammingDistance(hash1, hash2):
        return bin(abs(hash1) ^ abs(hash2)).count("1")

    def distanceTo(self, h):
        return Hash.hammingDistance(self._value, h._value)

    def percentsTo(self, h):
        return ((64 - self.distanceTo(h)) * 100.0) / 64.0

    def get_key_point(self):
        p = self.img.parent()
        px = int(p["x"]) if p else 0
        py = int(p["y"]) if p else 0
        return px, py

    def dict(self):
        p = self.img.parent()
        px = int(p["x"]) if p else 0
        py = int(p["y"]) if p else 0
        return {"x": px, "y": py, "width": self.img.width, "height": self.img.height}
