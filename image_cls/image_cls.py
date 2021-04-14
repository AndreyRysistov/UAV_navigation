import cv2
import math
from scipy import ndimage
import numpy as np


class Image(object):
    _img = None
    _parent = None

    def __init__(self, img):
        self._img = img

    def rotated_crop(self, center, size, angle_rad):
        half_height = size[1] // 2
        half_width = size[0] // 2
        up = np.array([int(math.sin(angle_rad) * half_height), int(math.cos(angle_rad) * half_height)])
        right = np.array([int(-math.cos(angle_rad) * half_width), int(math.sin(angle_rad) * half_width)])
        tl_point = center + up - right
        tr_point = center + up + right
        bl_point = center - up - right
        br_point = center - up + right
        points_x = (tl_point[0], tr_point[0], bl_point[0], br_point[0])
        points_y = (tl_point[1], tr_point[1], bl_point[1], br_point[1])

        left_corner = int(min(points_x))
        right_corner = int(max(points_x))
        bottom_corner = int(min(points_y))
        top_corner = int(max(points_y))
        crop_params = {
            'tl_point': tl_point,
            'tr_point': tr_point,
            'br_point': br_point,
            'bl_point': bl_point,
            'center': center,
            'up':up
        }
        crop_img = self._img[bottom_corner:top_corner, left_corner:right_corner]
        rotated = ndimage.rotate(crop_img, -math.degrees(angle_rad) + 180, reshape=True)
        horizontal_margin = max(rotated.shape[0] // 2 - half_width, 0)
        vertical_margin = max(rotated.shape[1] // 2 - half_height, 0)
        rotated_crop = rotated[vertical_margin: rotated.shape[1] - vertical_margin,
                       horizontal_margin: rotated.shape[1] - horizontal_margin]
        rotated_crop = rotated_crop[0:size[1], 0:size[0]]
        return Image(rotated_crop), crop_params

    def get_tiles(self, tile_size=(1024, 1024)):
        w, h, _ = self.shape
        w_new, h_new = tile_size
        step_w, step_h = int(w / w_new), int(h / h_new)
        tiles = []
        for i in range(step_w):
            for j in range(step_h):
                if i != step_w and j != step_h:
                    x1, y1 = w // step_w * i, h // step_h * j
                    x2, y2 = w // step_w * (i + 1), h // step_h * (j + 1)
                    tiles.append({'coordinates': (x1, y1, x2, y2), 'image_cls': self.crop(x1, y1, x2, y2)})
        return tiles

    def grayscale(self):
        return Image(cv2.cvtColor(self._img, cv2.COLOR_BGR2GRAY))

    def resize(self, size, inter=cv2.INTER_NEAREST):
        return Image(cv2.resize(self._img, size, interpolation=inter))

    @staticmethod
    def read(filename, channel=1):
        i = cv2.imread(filename, channel)
        if i is None:
            raise Exception("Could not read file: ", filename)

        return Image(i)

    @property
    def shape(self):
        return self._img.shape

    @property
    def width(self):
        return self.shape[1]

    @property
    def height(self):
        return self.shape[0]

    @property
    def img(self):
        return self._img

    def pixel(self, x, y):
        return self._img[x, y]

    def show(self, delay=0):
        cv2.imshow('Show image_cls', self._img)
        cv2.waitKey(delay)

    def parent(self, parent=None, x=None, y=None):
        if x or y or parent:
            self._parent = {"img": parent, 'x': int(x), 'y': int(y)}
            return self

        return self._parent

    def crop(self, x1, y1, x2, y2):
        cropped = self._img[y1:y2, x1:x2]
        if len(cropped) == 0:
            return False

        i = Image(cropped)
        i.parent(self, x1, y1)

        return i
