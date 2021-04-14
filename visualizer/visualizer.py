import cv2


class Visualizer:

    def __init__(self, landscape_map):
        #self.config = config
        self.landscape_map = landscape_map.img
        self.landscape_map_debug = self.landscape_map.copy()

    def draw_trajectory(self, xsmooth, ysmooth):
        for i in range(len(xsmooth)):
            cv2.circle(self.landscape_map, (int(xsmooth[i]), int(ysmooth[i])), 4, (0, 0, 255), -1)

    def draw_line_moving(self, prev, current, color=(255, 255, 255), size=8):
        cv2.line(self.landscape_map, prev, current, color, size)

    def draw_destination(self, destination):
        cv2.circle(self.landscape_map, destination, 32, (0, 0, 255), 8)

    def draw_drone_area(self, picture_params, color=(0, 255, 0)):
        tl_point, tr_point = picture_params['tl_point'], picture_params['tr_point']
        br_point, bl_point = picture_params['br_point'], picture_params['bl_point']
        center, up = picture_params['center'], picture_params['up']
        cv2.line(self.landscape_map_debug, tuple(tl_point), tuple(tr_point), color, 4)
        cv2.line(self.landscape_map_debug, tuple(tr_point), tuple(br_point), color, 4)
        cv2.line(self.landscape_map_debug, tuple(br_point), tuple(bl_point), color, 4)
        cv2.line(self.landscape_map_debug, tuple(center), tuple(center + up), color, 4)
        cv2.circle(self.landscape_map_debug, tuple(center), 16, (0, 0, 255), -1)
        cv2.line(self.landscape_map_debug, tuple(bl_point), tuple(tl_point), color, 4)

    def draw_drone_moving(self, picture_params, position, detect_position):
        self.landscape_map_debug = self.landscape_map.copy()
        self.draw_drone_area(picture_params)
        cv2.circle(self.landscape_map_debug, detect_position, 16, (0, 255, 255), -1)
        cv2.line(self.landscape_map_debug, detect_position, position, (0, 255, 255), 4)
        cv2.circle(self.landscape_map_debug, position, 16, (255, 255, 255), -1)
        smaller_image = cv2.resize(self.landscape_map_debug, (800, 800))
        cv2.imshow('Result', smaller_image)
        cv2.waitKey(1)

    def draw_drone_picture(self, picture):
        cv2.imshow('Drone', picture.img)
        cv2.waitKey(1)

    def wait(self):
        cv2.waitKey(0)
        cv2.destroyAllWindows()