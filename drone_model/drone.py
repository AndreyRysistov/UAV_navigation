import time
import pickle
import numpy as np
import pprint
import math
import cv2
from drone_model.drone_picture import get_path_nodes, get_rotated_crop
from image import Image

class Drone:
    _tile_matrix = None
    _landscape_hashes = None

    def __init__(self, config, detector, landscape_map):
        self.config = config
        self._speed = self.config.drone.speed
        self._detector = detector
        self._landscape_map = landscape_map
        self._rotation = self.config.drone.rotation
        self._x = self.config.drone.x_start
        self._y = self.config.drone.y_start
        self._detectedpos = (self._x, self._y)

    def get_position_from_image(self, start_rotation = None):
        if (start_rotation is None):
            start_rotation = self._rotation
        candidates = self.find_candidates()
        img = self.get_picture(self.get_rotation())
        cv2.imshow('Drone', img)
        cv2.waitKey(1)
        image = Image(img)
        forward = self.get_forward_vector()
        if (len(candidates) > 5):
            x, y = self._detector.detect_position(image, candidates)
            if (x is not None and y is not None) and (self.get_distance_to_point((x + forward[0], y + forward[1])) > self._speed * 3):
                print('Detected point [{0}] too far, distance: {1}'.format(self.get_distance_to_point((x,y)), self.get_distance_to_point((x,y))))
                x, y = None, None
        else:
            x, y = (None, None)
        if (x is None or y is None or len(candidates) < 5 or (x == 0 and y == 0)):
            if ((x == 0 and y == 0)):
                print('Zero homogenous matrix.')
            if (len(candidates) < 5):
                print('Not enough candidates:' + str(len(candidates)))

        result = (x, y)

        if (x == None and y == None):
            result = (None, None)
            while (result is (None, None)):
                self._rotation += np.pi / 60
                if (start_rotation + self._rotation > np.pi * 2):
                    self._rotation = start_rotation
                    forward = self.get_forward_vector()
                    self.move(self._detectedpos + forward)
                print('Rotation! ' + str(math.degrees(self._rotation)))
                result = self.get_position_from_image(start_rotation=start_rotation)
        self._rotation = start_rotation
        self._detectedpos = result
        return result

    def find_candidates(self): # оптимизирвоать
        hashes = []

        forward = self.get_forward_vector()
        check_point = (self._detectedpos[0] + forward[0], self._detectedpos[1] + forward[1])
        
        check = lambda u, v: (u - check_point[0]) ** 2 + (v - check_point[1]) ** 2 <= self.config.drone.area ** 2

        tile_size = self.config.glob.tile_size
        map_size = self.config.glob.map_size

        left    = math.floor((check_point[0] - self.config.drone.area) / tile_size[0])
        right   = math.floor((check_point[0] + self.config.drone.area) / tile_size[0])
        bottom  = math.floor((check_point[1] - self.config.drone.area) / tile_size[1])
        top     = math.floor((check_point[1] + self.config.drone.area) / tile_size[1])

        left = max(min(left, int(map_size[0]/tile_size[0])), 0)
        right = max(min(right, int(map_size[0]/tile_size[0])), 0)
        bottom = max(min(bottom, int(map_size[1]/tile_size[1])), 0)
        top = max(min(top, int(map_size[1]/tile_size[1])), 0)

        coords = []

        for i in range(left, right + 1):
            for j in range(bottom, top + 1):
                coords.append((i*tile_size[0], j*tile_size[1], (i + 1)*tile_size[0], (j + 1)*tile_size[1]))

        for tile in self._landscape_hashes:
            if (tile['tile_coordinates'] in coords):
                for hash in tile['hashes']:
                    if check(int(hash.dict()['x']), int(hash.dict()['y'])):
                        hashes.append(hash)

        return hashes

    def load_hashes(self, path):
        with open(path, 'rb') as f:
            self._landscape_hashes = pickle.load(f)
        positions = [h['tile_coordinates'] for h in self._landscape_hashes]

    def move(self, destination):
        distance = self.get_distance_to_point(destination)
        current_angle = self._rotation
        angle_rad = math.atan2(destination[0]-self._detectedpos[0], destination[1]-self._detectedpos[1])
        if (abs(angle_rad) > np.pi): angle_rad += np.pi
        angle_limit = np.pi/6
        right_limit = current_angle + angle_limit
        left_limit = current_angle - angle_limit
        if (distance < self._speed):
            move_speed = distance
            current_angle = angle_rad
        else:
            move_speed = self._speed
            current_angle = max(min(angle_rad, right_limit), left_limit)
        self._rotation = angle_rad
        forward = self.get_forward_vector()
        self._x += forward[0]
        self._y += forward[1]
        self._detectedpos = (self._detectedpos[0] + forward[0], self._detectedpos[1] + forward[1])

    def get_distance_to_point(self, point):
        return math.sqrt((point[0]-self._detectedpos[0]) ** 2 + (point[1]-self._detectedpos[1]) ** 2)

    def get_forward_vector(self):
        return (math.sin(self._rotation)*self._speed, math.cos(self._rotation)*self._speed)

    def get_rotation(self):
        return self._rotation

    def get_position(self):
        return int(self._x), int(self._y)

    def get_picture(self, rotation):
        bottom_corner, top_corner, left_corner, right_corner, rotated_crop = get_rotated_crop(self._landscape_map.img, (self._x, self._y), self.config.drone.image_size, rotation)
        return rotated_crop


