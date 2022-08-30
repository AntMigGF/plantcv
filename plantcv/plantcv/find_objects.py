# Find Objects

import cv2
import numpy as np
import os
from plantcv.plantcv._debug import _debug
from plantcv.plantcv import params, Objects



def find_objects(img, mask):
    """
    Find all objects and color them blue.

    Inputs:
    img       = RGB or grayscale image data for plotting
    mask      = Binary mask used for contour detection


    Returns:
    objects   = plantcv.Objects class

    :param img: numpy.ndarray
    :param mask: numpy.ndarray
    :return objects: plantcv.Objects
    """
    mask1 = np.copy(mask)
    ori_img = np.copy(img)
    # If the reference image is grayscale convert it to color
    if len(np.shape(ori_img)) == 2:
        ori_img = cv2.cvtColor(ori_img, cv2.COLOR_GRAY2BGR)
    contour, hierarchy = cv2.findContours(mask1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
    # Cast tuple objects as a list
    contours = list(contour)
    for i, cnt in enumerate(contours):
        cv2.drawContours(ori_img, contours, i, (255, 102, 255), -1, lineType=8, hierarchy=hierarchy)
    objects = Objects(contours, hierarchy)

    _debug(visual=ori_img,
           filename=os.path.join(params.debug_outdir, str(params.device) + '_id_objects.png'))

    return objects
