from image_cls.image_cls import Image
from detectors.hash_detector import HashPointDetector
from utils.config import get_config_from_json
import numpy as np
from drone_model.drone import Drone
from trajectory.create_trajectory import get_path_nodes
from visualizer.visualizer import Visualizer
import time
import math
import cv2
from statistics import median
import random

path = np.array([[2524, 2200], [2640, 1500], [1614, 1200], [1900, 800]])# [2402, 1156], [456,2631], [3347, 2750]])
nodes, xsmooth, ysmooth = get_path_nodes(path, spline_step=512, smoothness=3, path_step=300)
print(nodes)
mse = lambda v, u: np.sqrt((u[0] - v[0]) ** 2 + (u[1] - v[1]) ** 2)
detect_real_errors = []
trajectory_real_errors = []
times_detecting = []


def main():
    detector_config = get_config_from_json('configs/orb_config.json')
    drone_config = get_config_from_json('configs/drone_config.json')
    glob_config = get_config_from_json('configs/glob_config.json')
    landscape_map = Image.read(glob_config.path_to_map)
    detector = HashPointDetector(detector_config)
    drone = Drone(drone_config, glob_config, detector, landscape_map)
    drone.load_hashes(detector.config.path_to_hashes)
    visualizer = Visualizer(landscape_map)
    visualizer.draw_trajectory(xsmooth, ysmooth)
    position = drone.get_position()

    shift = random.random()*100.0

    count_step = 0
    for node in nodes:
        destination = node['point']
        detect_position = drone.get_position_from_image()
        while drone.get_distance_to_point(destination) > 32:
            prev_position = drone.get_position()
            visualizer.draw_line_moving(prev_position, position)
            position = drone.get_position()
            if count_step % 4 == 0:
                print('Take picture')
                position = drone.get_position()
                start_time = time.time()
                detect_position = drone.get_position_from_image()
                mse_value = mse(position, detect_position)
                detect_real_errors.append(mse_value)
                visualizer.dashboard_text(4, 'MSE: {}'.format(mse_value))
                time_detecting = time.time() - start_time
                visualizer.dashboard_text(5, 'Time: {}'.format(time_detecting))
                times_detecting.append(time_detecting)
            visualizer.init_debug_frame()
            visualizer.draw_destination(destination)
            picture_params = drone.get_picture_params()
            visualizer.update_landscape_debug_frame()
            drone.move(destination)
            visualizer.draw_drone_moving(picture_params, position, drone.real_pos, detect_position)
            visualizer.draw_drone_picture(drone.get_picture())
            visualizer.dashboard_text(0, 'Speed: {}'.format(float(drone.get_speed())))
            visualizer.dashboard_text(1, 'Height: {}'.format(200.0+15*math.sin(shift + time.time()*0.017)+7*math.cos(shift*13 + time.time()*0.15)))
            visualizer.dashboard_text(2, 'Angle: {}'.format(math.degrees(abs(drone.get_rotation()))))
            visualizer.dashboard_text(3, 'Keypoints: {}'.format(drone.cur_candidates))
            visualizer.dashboard_text(6, 'Average MSE: {}'.format(median(detect_real_errors)))
            visualizer.dashboard_text(7, 'Average time: {}'.format(median(times_detecting)))
            count_step +=1
            cv2.waitKey(50)
    print('Detect-real MSE: ', sum(detect_real_errors) / len(detect_real_errors))
    print('Mean time detecting: ', sum(times_detecting) / len(times_detecting))
    visualizer.wait()





if __name__ == '__main__':
    main()

