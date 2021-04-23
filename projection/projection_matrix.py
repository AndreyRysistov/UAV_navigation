import cv2
import numpy as np


def get_transformed_point(transformation_matrix, point):
    homg_point = np.array((point[0], point[1], 1))
    transformed_homg_point = transformation_matrix.dot(homg_point)
    if (transformed_homg_point[2] != 0):
        transformed_homg_point /= transformed_homg_point[2]
    return (int(transformed_homg_point[0]), int(transformed_homg_point[1]))


def get_transformation_matrix(model_coords, image_coords):
    image_coords = np.array(image_coords, dtype="float32")
    model_coords = np.array(model_coords, dtype="float32")
    return cv2.getPerspectiveTransform(image_coords, model_coords)


def transform_point(model_coords, image_coords, point):
    """
        Parameters
        ----------
        model_coords : tuple
            4 coordiantes on model.
        image_coords : tuple
            4 same coordinates on image_cls in order.
        point : tuple
            Point to transform from image_cls to model.
    """
    matrix = get_transformation_matrix(model_coords, image_coords)
    return get_transformed_point(matrix, point)