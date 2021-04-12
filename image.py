import cv2

class Image(object):
    _img = None
    _parent = None

    def __init__(self, img):
        self._img = img

    @staticmethod
    def read(filename, channel=1):
        i = cv2.imread(filename, channel)
        if i is None:
            raise Exception("Could not read file: ", filename)

        return Image(i)

    def grayscale(self):
        return Image(cv2.cvtColor(self._img, cv2.COLOR_BGR2GRAY))

    def resize(self, size, inter=cv2.INTER_NEAREST):
        return Image(cv2.resize(self._img, size, interpolation=inter))

    @property
    def shape(self):
        return self._img.shape

    @property
    def width(self):
        return self.shape[1]

    @property
    def height(self):
        return self.shape[0]

    @property
    def img(self):
        return self._img

    def pixel(self, x, y):
        return self._img[x, y]

    def show(self):
        cv2.imshow('Show image', self._img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_tiles(self, tile_size=(1024, 1024, 3)):
        w, h, _ = self.shape
        w_new, h_new, _ = tile_size
        step_w, step_h = int(w /w_new), int(h / h_new)
        tiles = []
        for i in range(step_w):
            for j in range(step_h):
                if i != step_w and j != step_h:
                    x1, y1 = w // step_w * i, h // step_h * j
                    x2, y2 = w // step_w * (i + 1), h // step_h * (j + 1)
                    tiles.append({'coordinates': (x1, y1, x2, y2), 'image': self.crop(x1, y1, x2, y2)})
        return tiles

    def parent(self, parent=None, x=None, y=None):
        if x or y or parent:
            self._parent = {"img": parent, 'x': int(x), 'y': int(y)}
            return self

        return self._parent

    def crop(self, x1, y1, x2, y2):
        cropped = self._img[y1:y2, x1:x2]
        if len(cropped) == 0:
            return False

        i = Image(cropped)
        i.parent(self, x1, y1)

        return i
