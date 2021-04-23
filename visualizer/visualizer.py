import cv2
import numpy as np


class Visualizer:

    def __init__(self, landscape_map):
        self.dashboard = np.zeros((255, 512, 3), np.uint8)
        self.landscape_map_debug = landscape_map.img.copy()
        self.landscape_map_debug_frame = self.landscape_map_debug.copy()

    def draw_trajectory(self, xsmooth, ysmooth):
        for i in range(len(xsmooth)):
            cv2.circle(self.landscape_map_debug, (int(xsmooth[i]), int(ysmooth[i])), 4, (0, 0, 255), -1)

    def init_debug_frame(self):
        self.landscape_map_debug_frame = self.landscape_map_debug.copy()
        self.update_landscape_debug_frame()

    def draw_line_moving(self, prev, current, color=(255, 255, 255), size=8):
        cv2.line(self.landscape_map_debug, prev, current, color, size)

    def draw_destination(self, destination):
        cv2.circle(self.landscape_map_debug_frame, destination, 32, (0, 0, 255), 8)
        self.update_landscape_debug_frame()

    def draw_drone_area(self, picture_params, color=(0, 255, 0)):
        tl_point, tr_point = picture_params['tl_point'], picture_params['tr_point']
        br_point, bl_point = picture_params['br_point'], picture_params['bl_point']
        center, up = picture_params['center'], picture_params['up']
        cv2.line(self.landscape_map_debug_frame, tuple(tl_point), tuple(tr_point), color, 4)
        cv2.line(self.landscape_map_debug_frame, tuple(tr_point), tuple(br_point), color, 4)
        cv2.line(self.landscape_map_debug_frame, tuple(br_point), tuple(bl_point), color, 4)
        cv2.line(self.landscape_map_debug_frame, tuple(center), tuple(center + up), color, 4)
        cv2.line(self.landscape_map_debug_frame, tuple(bl_point), tuple(tl_point), color, 4)

    def draw_drone_moving(self, picture_params, position, real_position, detect_position):
        position = (int(position[0]), int(position[1]))
        real_position = (int(real_position[0]), int(real_position[1]))
        detect_position = (int(detect_position[0]), int(detect_position[1]))
        difference = (detect_position[0] - real_position[0], detect_position[1] - real_position[1])
        actual_detectpos = (position[0] + difference[0] ,position[1] + difference[1])
        self.draw_drone_area(picture_params)
        cv2.circle(self.landscape_map_debug_frame, actual_detectpos, 16, (255, 255, 0), -1)
        cv2.circle(self.landscape_map_debug_frame, actual_detectpos, 32, (255, 255, 0), 4)
        cv2.line(self.landscape_map_debug_frame, position, actual_detectpos, (255, 255, 0), 4)
        cv2.circle(self.landscape_map_debug_frame, position, 16, (255, 255, 255), -1)
        self.update_landscape_debug_frame()

    def update_landscape_debug_frame(self):
        smaller_image = cv2.resize(self.landscape_map_debug_frame, (800, 800))
        cv2.imshow('Result', smaller_image)
        cv2.waitKey(1)

    def update_dashboard(self):
        cv2.imshow('Dashboard', self.dashboard)
        cv2.waitKey(1)

    def draw_drone_picture(self, picture):
        cv2.imshow('Drone', picture.img)
        cv2.waitKey(1)

    def wait(self):
        cv2.waitKey(0)

    def dashboard_text(self, row, text):
        point = (12, 24 + 24*row)
        self.dashboard[12 + 24*row : 12 + 24*(row+1),0:512] = (0,0,0)
        font_scale = 1
        font = cv2.FONT_HERSHEY_PLAIN
        cv2.putText(self.dashboard,text,point,font,fontScale=font_scale,color=(255,255,255),thickness=1)
        self.update_dashboard()
    
    def circle(self, point, scale, color, thickness):
        point = (int(point[0]), int(point[1]))
        cv2.circle(self.landscape_map_debug_frame, point, int(scale), color, thickness)
        self.update_landscape_debug_frame()