from projection.projection_matrix import *
from hash.extract import *
from hash.match import Match


class HashPointDetector:
    _algorithms = {
        "ORB": cv2.ORB_create,
        "SIFT": cv2.xfeatures2d.SIFT_create,
        "SURF": cv2.xfeatures2d.SURF_create
    }
    _tile_matrix = None
    _landscape_hashes = None

    def __init__(self, config):
        self.config = config
        self._algorithm_name = self.config.detector.algorithm.upper()
        self._algorithm = self._algorithms[self._algorithm_name](**self.config.detector.params)

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
        current_hash = get_hashes(bin_images)
        matches = HashPointDetector.match(current_hash, land_hash, self.config.detector.limit_distance)
        sort_match = sorted(matches, key= lambda match: match.distance)[:4]
        landscape_points = [point.hashes[1].get_key_point() for point in sort_match]
        image_points = [point.hashes[0].get_key_point() for point in sort_match]
        # image_land = cv2.imread('images_unity/map/image_400_400_0.png')
        # for point1, point2 in zip(landscape_points, image_points):
        #     print('landscape: {}, image: {}'.format(point1, point2))
        #     cv2.circle(image_land, point1, 3, (0, 0, 255), -1)
        #     cv2.circle(image.img, point2, 3, (255, 0, 0), -1)
        # cv2.circle(image.img, (x, y), 3, (255, 255, 0), -1)
        # cv2.circle(image_land, (transform_point(landscape_points, image_points, (x, y))), 3, (255, 255, 0), -1)
        # #image = cv2.resize(image.img, (1024, 1024))
        # image_land = image_land[1022:2024, 1824:2848]
        # cv2.imshow('Land', image_land)
        # cv2.imshow('Image', image.img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return transform_point(landscape_points, image_points, (x, y))

    def get_key_points(self, image:np.array):
        kp, _ = self.create_features(image)
        return kp

    def get_descriptors(self, image:np.array):
        _, des = self.create_features(image)
        return des

    def get_config(self):
        return self.config.detector.params.ToDict()

    @staticmethod
    def match(hs1, hs2, distance=None):
        result = []
        for h1 in hs1:
            for h2 in hs2:
                matched = h1 == h2 if distance is None else h1.distanceTo(h2) <= distance
                if matched:
                    result.append(Match(h1, h2))
        return result





