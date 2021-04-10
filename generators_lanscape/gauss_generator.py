import numpy as np
import random


class GaussGeneratorLandscape:
    def __init__(self, config):
        self.config = config
        self.n, self.m = self.config.generator.size

    def generate_landscape(self, seed):
        map_height = np.zeros(shape=self.config.generator.size)
        random.seed(seed)
        count_mounts = random.uniform(self.config.generator.count_mounts)
        for _ in range(count_mounts):
            x = np.linspace(0, self.m, self.m)
            y = np.linspace(0, self.n, self.n)

            x, y = np.meshgrid(x, y)
            mx = random.uniform(*tuple(self.config.generator.tx_range))
            my = random.uniform(*tuple(self.config.generator.ty_range))
            sx = random.uniform(*tuple(self.config.generator.px_range))
            sy = random.uniform(*tuple(self.config.generator.py_range))
            amplitude = random.uniform(*tuple(self.config.generator.amplitude_range))
            alpha = np.pi/180 * random.uniform(-90, 90)
            xs = x * np.cos(alpha) - y * np.sin(alpha)
            ys = x * np.sin(alpha) + y * np.cos(alpha)
            map_height += amplitude * GaussGeneratorLandscape._gaussian(xs, ys, mx=mx, my=my, sx=sx, sy=sy)
            map_height = GaussGeneratorLandscape._project(map_height,
                                                          (map_height.min(), map_height.max()),
                                                          self.config.generator.rescale)
        return x, y, map_height

    @staticmethod
    def _project(values, diap_a, diap_b):
        relative_value = (values - diap_a[0]) / (diap_a[1] - diap_a[0])
        scaled_value = diap_b[0] + (diap_b[1] - diap_b[0]) * relative_value
        return scaled_value

    @staticmethod
    def _gaussian(x, y, mx=0, my=0, sx=1, sy=1):
        return np.exp(-((x - mx)**2. / (2. * sx**2.) + (y - my)**2. / (2. * sy**2.)))