import os
import pickle
from utils.config import get_config_from_json
from detectors.hash_detector import HashPointDetector
from hash.extract import *
import pprint


def create_hashes(tiles, detector):
    result = []
    for tile in tiles:
        dx, dy, _, _ = tile['coordinates']
        kp, des = detector.create_features(tile['image'].img)
        for key_point in kp:
            key_point.pt = (key_point.pt[0]+dx, key_point.pt[1]+dy)
        image_bin = binImages(kp, des)
        hashes = get_hashes(image_bin)
        result.append({
            'tile_coordinates': tile['coordinates'],
            'hashes': hashes
        })
    return result


if __name__ == '__main__':
    config, _ = get_config_from_json('configs/orb_config.json')
    landscape_map = Image.read(os.path.join('images_unity', 'map', 'image_400_400_0.png'))
    detector = HashPointDetector(config)
    tiles = landscape_map.get_tiles(tile_size=(512, 512, 3))
    detector = HashPointDetector(config)
    landscape_hashes = create_hashes(tiles, detector)
    with open(config.glob.path_des, 'wb') as des_file:
        pickle.dump(landscape_hashes, des_file)
    print('Done!')