from image_cls.image_cls import Image
from detectors.hash_detector import HashPointDetector
from utils.config import get_config_from_json
import numpy as np
from drone_model.drone import Drone
from trajectory.create_trajectory import get_path_nodes
from visualizer.visualizer import Visualizer
import time

path = np.array([[2524, 2200], [2640, 1500], [1614, 1200], [1900, 800]])# [2402, 1156], [456,2631], [3347, 2750]])
nodes, xsmooth, ysmooth = get_path_nodes(path, spline_step=256, smoothness=3, path_step=200)
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
    count_step = 0
    for node in nodes:
        destination = node['point']
        detect_position = drone.get_position_from_image()
        while drone.get_distance_to_point(destination) > 20:

            visualizer.draw_destination(destination)
            prev_position = drone.get_position()
            visualizer.draw_line_moving(prev_position, position)
            position = drone.get_position()

            if count_step %4 == 0:
                print('Take picture')
                position = drone.get_position()
                start_time = time.time()
                detect_position = drone.get_position_from_image()
                detect_real_errors.append(mse(position, detect_position))
                time_detecting = time.time() - start_time
                times_detecting.append(time_detecting)
                picture_params = drone.get_picture_params()
                visualizer.draw_drone_moving(picture_params, position, detect_position)
            visualizer.draw_drone_picture(drone.get_picture())
            drone.move(destination)
            count_step +=1
    print('Detect-real MSE: ', sum(detect_real_errors) / len(detect_real_errors))
    print('Mean time detecting: ', sum(times_detecting) / len(times_detecting))
    visualizer.wait()





if __name__ == '__main__':
    main()

