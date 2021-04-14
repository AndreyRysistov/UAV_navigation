import time
import pickle
import numpy as np
import math


class Drone:
    _landscape_hashes = None
    _picture = None
    _picture_params = None

    def __init__(self, drone_config, glob_config, detector, landscape_map):
        self._detector = detector
        self._landscape_map = landscape_map
        self.config = drone_config
        self.glob_config = glob_config
        self._speed = self.config.speed
        self._max_speed = self._speed
        self._rotation = self.config.rotation
        self._x = self.config.x_start
        self._y = self.config.y_start
        self._detected_pos = (self._x, self._y)

    def get_position_from_image(self, start_rotation=None):
        if start_rotation is None:
            start_rotation = self._rotation
        self._picture, self._picture_params = self.take_picture()
        candidates = self.find_candidates()
        forward = self.get_forward_vector()
        if len(candidates) > 3:
            x, y = self._detector.detect_position(self._picture, candidates)
            if (x is not None and y is not None) and (
                    self.get_distance_to_point((x + forward[0], y + forward[1])) > self._speed * 3):
                print('Detected point [{0}] too far, distance: {1}'.format((x, y), self.get_distance_to_point((x, y))))
                x, y = None, None
        else:
            print('Not enough candidates:' + str(len(candidates)))
            x, y = None, None
        while x is None and y is None:
            self._rotation += np.pi / 6
            if start_rotation + self._rotation > np.pi*2:
                self._rotation = start_rotation
                forward = self.get_forward_vector()
                self.move(self.get_position() + forward)
            #print('Rotation! ' + str(math.degrees(self._rotation)))
            x, y = self.get_position_from_image(start_rotation=start_rotation)
        self._rotation = start_rotation
        self._detected_pos = x, y
        return x, y

    def find_candidates(self):
        hashes = []
        forward = self.get_forward_vector()
        check_point = (self._detected_pos[0] + forward[0], self._detected_pos[1] + forward[1])
        check = lambda u, v: (u - check_point[0]) ** 2 + (v - check_point[1]) ** 2 <= self.config.area ** 2
        tile_size = self.glob_config.tile_size
        map_size = self.glob_config.map_size
        left = math.floor((check_point[0] - self.config.area) / tile_size[0])
        right = math.floor((check_point[0] + self.config.area) / tile_size[0])
        bottom = math.floor((check_point[1] - self.config.area) / tile_size[1])
        top = math.floor((check_point[1] + self.config.area) / tile_size[1])
        left = max(min(left, int(map_size[0] / tile_size[0])), 0)
        right = max(min(right, int(map_size[0] / tile_size[0])), 0)
        bottom = max(min(bottom, int(map_size[1] / tile_size[1])), 0)
        top = max(min(top, int(map_size[1] / tile_size[1])), 0)
        coordinates = []
        for i in range(left, right + 1):
            for j in range(bottom, top + 1):
                coordinates.append((i * tile_size[0], j * tile_size[1], (i + 1) * tile_size[0], (j + 1) * tile_size[1]))
        for tile in self._landscape_hashes:
            if tile['tile_coordinates'] in coordinates:
                for h in tile['hashes']:
                    if check(int(h.dict()['x']), int(h.dict()['y'])):
                        hashes.append(h)
        return hashes

    def move(self, destination):
        distance = self.get_distance_to_point(destination)
        current_angle = self._rotation
        angle_rad = math.atan2(destination[0] - self._detected_pos[0], destination[1] - self._detected_pos[1])
        if abs(angle_rad) > np.pi:
            angle_rad += np.pi
        angle_limit = np.pi / 180 * self.config.angle_limit
        right_limit = current_angle + angle_limit
        left_limit = current_angle - angle_limit
        if distance < self._speed:
            self._speed = distance
            current_angle = angle_rad
        else:
            self._speed = self._max_speed
            current_angle = max(min(angle_rad, right_limit), left_limit)
        self._rotation = angle_rad
        forward = self.get_forward_vector()
        self._x, self._y = (self._x + forward[0], self._y + forward[1])
        self._detected_pos = (self._detected_pos[0] + forward[0], self._detected_pos[1] + forward[1])
        print('Update position: {}'.format(self._detected_pos))

    def get_distance_to_point(self, point):
        return math.sqrt((point[0] - self._detected_pos[0]) ** 2 + (point[1] - self._detected_pos[1]) ** 2)

    def get_forward_vector(self):
        return math.sin(self._rotation) * self._speed, math.cos(self._rotation) * self._speed

    def get_rotation(self):
        return self._rotation

    def get_position(self):
        return int(self._x), int(self._y)

    def get_picture(self):
        return self._picture

    def get_picture_params(self):
        return self._picture_params

    def take_picture(self):
        return self._landscape_map.rotated_crop(
            center=(self.get_position()[0], self.get_position()[1]),
            size=self.config.image_size,
            angle_rad=self._rotation
        )

    def load_hashes(self, path):
        print(path)
        with open(path, 'rb') as f:
            self._landscape_hashes = pickle.load(f)
