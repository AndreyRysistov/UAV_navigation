import numpy as np
from scipy.interpolate import splprep, splev
import math


def get_path_nodes(path, spline_step, smoothness, path_step):
    x = path[:, 0]
    y = path[:, 1]
    distance = 0
    for i in range(len(path)):
        point = (path[i][0], path[i][1])
        if i != 0:
            prev_point = (path[i - 1][0], path[i - 1][1])
        else:
            prev_point = None
        if prev_point is not None:
            distance += math.sqrt((point[0] - prev_point[0]) ** 2 + (point[1] - prev_point[1]) ** 2)

    tck, u = splprep([x, y], s=0, k=1)
    xnew, ynew = splev(np.linspace(0, 1, int(distance / spline_step)), tck, der=0)

    tck1, u1 = splprep([xnew, ynew], s=0, k=3)  # smooth line
    xsmooth, ysmooth = splev(np.linspace(0, 1, int(distance / smoothness)), tck1, der=0)

    nodes = []

    count = 0
    for i in range(len(xsmooth)):
        count += smoothness / path_step
        point = (xsmooth[i], ysmooth[i])
        if i != 0:
            prev_point = (xsmooth[i - 1], ysmooth[i - 1])
        else:
            prev_point = None
        if prev_point is None:
            radians = 0
        else:
            radians = math.atan2(point[0] - prev_point[0], point[1] - prev_point[1])
        if count > 1:
            count = 0;
            nodes.append({'point': (int(point[0]), int(point[1])), 'angle_rad': radians})
    return nodes, xsmooth, ysmooth