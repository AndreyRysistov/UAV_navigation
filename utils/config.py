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
    return config