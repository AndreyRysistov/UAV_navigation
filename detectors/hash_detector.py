from projection.projection_matrix import *
from hash.extract import *
from hash.match import Match
import time


class HashPointDetector:
    _algorithms = {
        "ORB": cv2.ORB_create,
        "SIFT": cv2.xfeatures2d.SIFT_create,
        #"SURF": cv2.xfeatures2d.SURF_create
    }
    _landscape_hashes = None

    def __init__(self, config):
        self.config = config
        self._algorithm_name = self.config.algorithm.upper()
        self._algorithm = self._algorithms[self._algorithm_name](**self.config.params)

    def create_features(self, image: np.array):
        if self._algorithm_name == 'ORB' or self._algorithm_name == 'SIFT':
            kp, des = self._algorithm.detectAndCompute(image, None)
        else:
            pass
        return kp, des

    def detect_position(self, image, land_hash):
        x, y = image.width//2, image.height//2
        kp, des = self.create_features(image.img)
        bin_images = binImages(kp, des)
        current_hashes = get_hashes(bin_images)
        processed_hashes = current_hashes.copy()

        for i in range(len(current_hashes)):
            for j in range(i+1, len(current_hashes)):
                point_cur = current_hashes[i].get_key_point() # image_point
                point_check = lambda point: (point[0] - point_cur[0]) ** 2 + (point[1] - point_cur[1]) ** 2 < 16 ** 2
                if point_check(current_hashes[j].get_key_point()):
                    if current_hashes[j] in processed_hashes:
                        processed_hashes.remove(current_hashes[j])

        matches = HashPointDetector.match(processed_hashes, land_hash, self.config.limit_distance)

        sort_match = sorted(matches, key=lambda match: match.distance)[:4]
        landscape_points = [point.hashes[1].get_key_point() for point in sort_match]
        image_points = [point.hashes[0].get_key_point() for point in sort_match]

        if len(image_points) < 4:
            print('Not enoigh image_points: ' + str(len(image_points)))
            return None, None

        return transform_point(landscape_points, image_points, (x, y))

    def get_key_points(self, image: np.array):
        kp, _ = self.create_features(image)
        return kp

    def get_descriptors(self, image: np.array):
        _, des = self.create_features(image)
        return des

    def get_config(self):
        return self.config.ToDict()

    @staticmethod
    def match(hs1, hs2, distance=None):
        result = []
        for h1 in hs1:
            for h2 in hs2:
                matched = h1 == h2 if distance is None else h1.distanceTo(h2) <= distance
                if matched:
                    result.append(Match(h1, h2))
        return result





