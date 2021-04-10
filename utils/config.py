import json
from dotmap import DotMap
import os


def get_config_from_json(json_file):
    """
    Get the generator_config.json from a json file
    :param json_file:
    :return: generator_config.json(namespace) or generator_config.json(dictionary)
    """
    with open(json_file, 'r') as config_file:
        config_dict = json.load(config_file)
    config = DotMap(config_dict)
    config.visualizer.log_dir.map_3d = os.path.join("images_gauss", "map_3d", config.exp)
    config.visualizer.log_dir.contour_map = os.path.join("images_gauss", "contour_map", config.exp)
    config.visualizer.log_dir.heat_map = os.path.join("images_gauss", "heat_map", config.exp)
    return config, config_dict