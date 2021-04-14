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
        kp, des = detector.create_features(tile['image_cls'].img)
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
    detector_config = get_config_from_json('configs/orb_config.json')
    glob_config = get_config_from_json('configs/glob_config.json')
    landscape_map = Image.read(glob_config.path_to_map)
    detector = HashPointDetector(detector_config)
    tiles = landscape_map.get_tiles(tile_size=glob_config.tile_size)
    landscape_hashes = create_hashes(tiles, detector)
    with open(detector.config.path_to_hashes, 'wb') as des_file:
        pickle.dump(landscape_hashes, des_file)
    print('Done!')



# def create_hashes(tiles, detector):
#     result = []
#     for tile in tiles:
#         dx, dy, _, _ = tile['coordinates']
#         sub_tiles = tile['image_cls'].get_tiles(tile_size=(
#             glob_config.tile_size[0] // 2,
#             glob_config.tile_size[1] // 2)
#         )
#         tile_hashes = []
#         for sub_tile in sub_tiles:
#             kp, des = detector.create_features(sub_tile['image_cls'].img)
#             for key_point in kp:
#
#                 key_point.pt = (key_point.pt[0]+dx, key_point.pt[1]+dy)
#                 print(key_point.pt)
#             print(len())
#             image_bin = binImages(kp, des)
#             hashes = get_hashes(image_bin)
#             tile_hashes.extend(hashes)
#         result.append({
#             'tile_coordinates': tile['coordinates'],
#             'hashes': tile_hashes
#         })
#         #pprint.pprint()
#         break
#     return result