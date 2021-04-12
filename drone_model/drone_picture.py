import numpy as np
from scipy.interpolate import splprep, splev
from scipy import ndimage
import matplotlib.pyplot as plt
import math
import cv2
import os

def get_rotated_crop(image, center, size, angle_rad, debugImage = None):
    x = center[0]
    y = center[1]
    half_height = size[1]//2
    half_width = size[0]//2
    up = np.array([int(math.sin(angle_rad)*half_height), int(math.cos(angle_rad)*half_height)])
    right = np.array([int(-math.cos(angle_rad)*half_width), int(math.sin(angle_rad)*half_width)])
    tl_point = center + up - right
    tr_point = center + up + right
    bl_point = center - up - right
    br_point = center - up + right
    points_x = (tl_point[0], tr_point[0], bl_point[0], br_point[0])
    points_y = (tl_point[1], tr_point[1], bl_point[1], br_point[1])

    left_corner = int(min(points_x))
    right_corner = int(max(points_x))
    bottom_corner = int(min(points_y))
    top_corner = int(max(points_y))

    if (debugImage is not None):
        cv2.line(debugImage, tuple(tl_point), tuple(tr_point), (0,255,0),4)
        cv2.line(debugImage, tuple(tr_point), tuple(br_point), (0,255,0),4) 
        cv2.line(debugImage, tuple(br_point), tuple(bl_point), (0,255,0),4)
        cv2.line(debugImage, tuple(center), tuple(center + up), (0,255,0),4)

        cv2.circle(debugImage, tuple(center), 16, (0,0,255), -1)
        cv2.line(debugImage, tuple(bl_point), tuple(tl_point), (0,255,0),4)

    crop_img = image[bottom_corner:top_corner, left_corner:right_corner]

    rotated = ndimage.rotate(crop_img, -math.degrees(angle_rad)+180, reshape = True)

    horizontal_margin = max(rotated.shape[0]//2 - half_width, 0)
    vertical_margin =  max(rotated.shape[1]//2 - half_height, 0)

    r_bottom = math.floor(vertical_margin)
    r_top = math.floor(rotated.shape[1] - vertical_margin)
    r_left = math.floor(horizontal_margin)
    r_right = math.floor(rotated.shape[1] - horizontal_margin)

    rotated_crop = rotated[vertical_margin : rotated.shape[1] - vertical_margin, horizontal_margin : rotated.shape[1] - horizontal_margin]
    rotated_crop = rotated_crop[0:size[1], 0:size[0]]
    return bottom_corner, top_corner, left_corner, right_corner, rotated_crop

def get_path_nodes(path, spline_step, smoothness, image_step, image_size, debugImage = None):
    x = path[:,0]
    y = path[:,1]
    distance = 0

    for i in range(len(path)):
        point = (path[i][0], path[i][1])
        if (i != 0):
            prev_point = (path[i-1][0], path[i-1][1])
        else:
            prev_point = None
        if (debugImage is not None):
            cv2.circle(debugImage, point, 16, (200,0,0), -1)
        if (prev_point is not None):
            distance += math.sqrt((point[0] - prev_point[0])**2 + (point[1] - prev_point[1])**2)
            #if (debugImage is not None):
                #cv2.line(debugImage, point, prev_point, (100,0,0),8)

    tck, u = splprep( [x,y] ,s=0, k=1)
    xnew, ynew = splev( np.linspace( 0, 1, int(distance/spline_step) ), tck,der = 0)

    tck1, u1 = splprep( [xnew,ynew] ,s=0, k=3) # smooth line
    xsmooth, ysmooth = splev( np.linspace( 0, 1, int(distance/smoothness) ), tck1,der = 0)

    nodes = []

    count = 0
    for i in range(len(xsmooth)):
        count += smoothness / image_step
        if (debugImage is not None):
            cv2.circle(debugImage, (int(xsmooth[i]), int(ysmooth[i])), 4, (0,0,255), -1)
        point = (xsmooth[i], ysmooth[i])
        if (i != 0):
            prev_point = (xsmooth[i-1], ysmooth[i-1])
        else:
            prev_point = None
        if (prev_point is None):
            radians = 0
        else:
            radians = math.atan2(point[0]-prev_point[0], point[1]-prev_point[1])
        if (count > 1):
            count = 0;
            nodes.append({ 'point' : (int(point[0]), int(point[1])), 'angle_rad' : radians})
    return nodes

if __name__=='__main__':
    image = cv2.imread(os.path.abspath('image_400_400_0.png'))
    image_debug_path = image.copy()
    image_debug = image.copy()

    path = np.array([[640, 412], [949, 353], [512, 1054], [1942, 512], [2402, 1156], [456,2631], [3347, 2750]])

    SPLINE_STEP = 512 # spline node step (distance between spline nodes)
    SMOOTHNESS = 8 # spline step
    IMAGE_STEP = 256 # image step (distance between uav camera shots)
    IMAGE_SIZE = (300,300) # (size of uav camera shots)

    nodes = get_path_nodes(path, SPLINE_STEP, SMOOTHNESS, IMAGE_STEP, IMAGE_SIZE, image_debug_path)

    for node in nodes:
        image_debug = image_debug_path.copy()
        center = np.array([int(node['point'][0]), int(node['point'][1])])
        rad = node['angle_rad']
        if (node['take_shot']):
            rotated_crop = get_rotated_crop(image, center, IMAGE_SIZE, rad, debugImage=image_debug_path)
            cv2.imshow('Rotated crop', rotated_crop)
        else:
            cv2.circle(image_debug, tuple(center), 16, (0,0,255), -1)
        
        smaller_image = cv2.resize(image_debug, (1024,1024))
        cv2.imshow('Result', smaller_image)
        cv2.waitKey(delay=1)
    cv2.waitKey()