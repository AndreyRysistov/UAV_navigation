import os
from image import Image
from detectors.hash_detector import HashPointDetector
from utils.config import get_config_from_json
from drone_model.drone import Drone
import cv2
import numpy as np
from drone_model.drone_picture import get_path_nodes, get_rotated_crop
import math
from scipy import ndimage


if __name__ == '__main__':
    im_path = os.path.join('images_unity', 'map', 'image_400_400_0.png')
    config, _ =  get_config_from_json('configs/orb_config.json')
    landscape_map = Image.read(im_path)
    detector = HashPointDetector(config)
    drone = Drone(config, detector, landscape_map)
    drone.load_hashes(config.glob.path_des)

    image = cv2.imread(im_path)
    image_debug_path = image.copy()
    image_debug_frame = image.copy()

    SPLINE_STEP = 256 # spline node step (distance between spline nodes)
    SMOOTHNESS = 8 # spline step
    PATH_STEP = 200 # image step (distance between path nodes)
    
    path = np.array([[351, 855], [391, 1993], [2654, 3641]])

    nodes = get_path_nodes(path, SPLINE_STEP, SMOOTHNESS, PATH_STEP, debugImage = image_debug_path)

    pos = drone.get_position()
    prev_pos = (pos[0], pos[1])

    for node in nodes:
        destination = node['point']
        while (drone.get_distance_to_point(destination) > 64):
            pos = drone.get_position()
            cv2.line(image_debug_path, prev_pos, pos, (255,255,255), 8)
            image_debug_frame = image_debug_path.copy()
            cv2.circle(image_debug_frame, destination, 32, (0,0,255), 8)
            prev_pos = pos
            rotation = drone.get_rotation()
            bottom_corner, top_corner, left_corner, right_corner, rotated_crop = get_rotated_crop(image, pos, config.drone.image_size, rotation, debugImage=image_debug_frame)
            detect = drone.get_position_from_image()
            smaller_rotated = cv2.resize(rotated_crop, (512, 512))
            crop_debug = image_debug_frame[bottom_corner:top_corner, left_corner:right_corner]
            crop_debug_rotated = ndimage.rotate(crop_debug, -math.degrees(rotation)+180, reshape = True)
            smaller_crop = cv2.resize(crop_debug_rotated, (512, 512))
            both = cv2.hconcat((smaller_rotated, smaller_crop))
            cv2.imshow('Points', both)
            cv2.circle(image_debug_frame, detect, 16, (0,255,255), -1)
            cv2.line(image_debug_frame, detect, pos, (0,255,255), 4)
            cv2.circle(image_debug_frame, pos, 16, (255,255,255), -1)
            smaller_image = cv2.resize(image_debug_frame, (1024, 1024))
            cv2.imshow('Result', smaller_image)
            drone.move(destination)
            cv2.waitKey(1)
    cv2.waitKey()