import os
from image import Image
from detectors.hash_detector import HashPointDetector
from utils.config import get_config_from_json
from drone_model.drone import Drone


if __name__ == '__main__':
    config, _ = get_config_from_json('configs/orb_config.json')
    landscape_map = Image.read(os.path.join('images_unity', 'map', 'image_400_400_0.png'))
    detector = HashPointDetector(config)
    drone = Drone(config, detector, landscape_map)
    drone.load_hashes(config.glob.path_des)
    img = drone.take_picture()
    drone.get_position_from_image(img)