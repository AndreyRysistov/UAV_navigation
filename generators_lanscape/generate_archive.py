from generators_lanscape.gauss_generator import GaussGeneratorLandscape
from visualizer.plot_functions import Visualizer
from utils.config import get_config_from_json
from utils.dirs import create_dirs
from utils.utils import get_args


def main():
    args = get_args()
    config, _ = get_config_from_json(args.config)
    try:
        pass
    except Exception as err:
        print("missing or invalid arguments")
        exit(0)
    create_dirs([config.visualizer.log_dir.map_3d, config.visualizer.log_dir.contour_map, config.visualizer.log_dir.heat_map])
    generator = GaussGeneratorLandscape(config)
    visualizer = Visualizer(config)
    for i in range(config.glob.count_landscape_map):
        x, y, z = generator.generate_landscape(seed=i+10)
        visualizer.create_heatmap(z, file_name="landscape_{}.jpg".format(i))


if __name__ == '__main__':
    main()