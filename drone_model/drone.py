import time
import pickle
import numpy as np


class Drone:
    _tile_matrix = None
    _landscape_hashes = None

    def __init__(self, config, detector, map):
        self.config = config
        self.speed = self.config.drone.speed
        self._detector = detector
        self._map = map
        self._x = self.config.drone.x_start
        self._y = self.config.drone.y_start

    def get_position_from_image(self, image):
        start_time = time.time()
        candidates = self.find_candidates()
        x, y = self._detector.detect_position(image, candidates)
        self.update_position(x, y)
        print('Updated position x: {}, y: {}'.format(x, y))
        print('Time detecting: {}'.format(time.time() - start_time))

    def find_candidates(self):#слабое место
        hashes = []
        check = lambda u, v: (u - self._x) ** 2 + (v - self._y) ** 2 <= self.config.drone.area ** 2
        for tile in self._landscape_hashes:
            for hash in tile['hashes']:
                if check(int(hash.dict()['x']), int(hash.dict()['y'])):
                    hashes.append(hash)
        return hashes

    def load_hashes(self, path):
        with open(path, 'rb') as f:
            self._landscape_hashes = pickle.load(f)
        positions = [h['tile_coordinates'] for h in self._landscape_hashes]
        self._tile_matrix = np.array(positions).reshape((8, 8, 4))

    def take_picture(self):
        map_h, map_w, _ = self._map.shape
        dx = self._x - self.config.drone.area, self._x + self.config.drone.area
        dy = self._y - self.config.drone.area, self._y + self.config.drone.area
        x1 = dx[0] if dx[0] > 0 else 0
        x2 = dx[1] if dx[1] < map_w else map_w-self._x
        y1 = dy[0] if dy[0] > 0 else 0
        y2 = dy[1] if dy[1] < map_h else map_h - self._y
        return self._map.crop(x1, y1, x2, y2)

    def move(self, a, b):
        while np.sqrt((a[0] - b[0]) **2 + (a[1] - b[1])**2) > 1:
            self._x += self.speed

    def get_position(self):
        return self._x, self._y

    def update_position(self, x_new, y_new):
        self._x = x_new
        self._y = y_new


