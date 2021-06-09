import os
import math
import numpy as np
import cv2 as cv
from scipy import ndimage as ndi
from skimage.segmentation import watershed
#from skimage.measure import label

from plantcv import plantcv as pcv
#from plantcv.plantcv import fatal_error
from plantcv.plantcv import color_palette
from plantcv.plantcv import params
from plantcv.plantcv._debug import _debug


# to change for colorize_label_img once it's merged
def _labels2rgb(labels, n_labels, rgb_values):

    h,w = labels.shape
    rgb_img = np.zeros((h,w,3), dtype=np.uint8)
    for l in range(n_labels):
        rgb_img[labels == l+1] = rgb_values[l]

    return rgb_img


#def segment_image_series(img_dir, mask_dir, init_frame, save_labels=True, init_labels=None, ksize=3)
def segment_image_series(imgs_paths, masks_paths, init_img_name, save_labels=True, init_labels=None, ksize=3):
    """

    Inputs:
    img_dir     = Path to the image directory
    mask_dir    = Path to the mask directory
    init_frame  = Number of frame in the image series from where the labels propagate
    save_labels = Save the labels for each frame as a numpy array
    init_labels = Array containing the initialization labels (same shape as the images)
    ksize       = Size for the block of images considered at each frame

    Returns:
    out_labels       = 3D stack of segmented images

    :param img_dir: str
    :param mask_dir: str
    :param init_frame: int
    :param save_labels: bool
    :param init_labels: numpy.ndarray
    :param ksize: int
    :return out_labels: numpy.ndarray
    """
    debug = params.debug
    params.debug = None
    params.color_sequence = 'random'

    # for symmetry, using blocks (kernels) of size 2*floor(ksize/2) + 1
    half_k = math.floor(ksize/2)

    #image_names = sorted(os.listdir(img_dir))

    image_names = [os.path.basename(img_path) for img_path in imgs_paths]
    init_frame = image_names.index(init_img_name)

    if init_labels is None:
        #get initialization labels
        init_mask, _, _ = pcv.readimage(filename=masks_paths[init_frame])
        #init_mask, _, _ = pcv.readimage(filename=os.path.join(mask_dir,
        #                                f"{image_names[init_frame][:-4]}_mask.png"),
        #                                mode='gray')
        init_labels, _ = ndi.label(init_mask)

    # output initialization
    N = len(image_names)
    h, w = init_labels.shape
    out_labels = np.zeros((h,w,N),dtype=np.uint8)
    out_labels[:,:,init_frame] = init_labels

    n_labels = np.unique(init_labels).size - 1
    rgb_values = color_palette(n_labels)

    # propagate labels sequentially from init_frame
    # backward
    for n in range(init_frame,-1,-1):
        print(n)
        # build image and mask stacks
        d = 2*half_k+1
        img_stack = np.zeros((h,w,d))
        mask_stack = np.zeros((h,w,d))
        markers = np.zeros((h,w,d))
        # with this loop, the number of frames used is always the same,
        # if stack_idx is always initialized to 2*half_k the borders are 'constant'
        stack_idx = 2*half_k
        for m in range(half_k, -half_k-1, -1):
            frame = min(N-1, max(n+m,0))
            #img, _, _ = pcv.readimage(filename=os.path.join(img_dir,image_names[frame]))
            img, _, _ = pcv.readimage(filename=imgs_paths[frame])
            if m == 0:
                img_n_rgb = img
            mask, _, _ = pcv.readimage(filename=masks_paths[frame], mode='gray')
            #mask, _, _ = pcv.readimage(filename=os.path.join(mask_dir,
            #                            f"{image_names[frame][:-4]}_mask.png"),
            #                            mode='gray')
            img_stack[:,:,stack_idx] = pcv.rgb2gray(rgb_img=img)
            mask_stack[:,:,stack_idx] = mask
            markers[:,:,stack_idx] = out_labels[:,:,frame]
            stack_idx += -1

        # edges using 3D sobel operator as elevation map for watershed
        edges = ndi.generic_gradient_magnitude(img_stack, ndi.sobel)
        # segmentation using the watershed algorithm
        labels = watershed(edges, markers=markers, mask=mask_stack, compactness=0)
        out_labels[:,:,n] = labels[:,:,half_k]

        # Create images for plotting and printing (debug mode)
        rgb_seg = _labels2rgb(out_labels[:,:,n], n_labels, rgb_values)
        vis_seg = cv.addWeighted(img_n_rgb, 0.7, rgb_seg, 0.3, 0.0)
        params.debug = debug
        _debug(visual=vis_seg, filename=os.path.join(params.debug_outdir,
                                f"{str(params.device)}_{image_names[n][:-4]}_WSeg.png"))
        params.debug = None

    # forward
    for n in range(init_frame+1,N):
        print(n)
        # build image and mask stacks
        d = 2*half_k+1
        img_stack = np.zeros((h,w,d))
        mask_stack = np.zeros((h,w,d))
        markers = np.zeros((h,w,d))
        # with this loop, the number of frames used is always the same,
        # if stack_idx is always initialized to 0 the borders are 'constant'
        stack_idx = 0
        # if stack_idx is initialized this way, the laft border is 'zero padded'
        #stack_idx = -min(0,n-half_k)
        for m in range(-half_k,half_k+1):
            frame = min(N-1, max(n+m,0))
            img, _, _ = pcv.readimage(filename=imgs_paths[frame])
            #img, _, _ = pcv.readimage(filename=os.path.join(img_dir,image_names[frame]))
            if m == 0:
                img_n_rgb = img
            mask, _, _ = pcv.readimage(filename=masks_paths[frame], mode='gray')
            #mask, _, _ = pcv.readimage(filename=os.path.join(mask_dir,
            #                            f"{image_names[frame][:-4]}_mask.png"),
            #                            mode='gray')
            img_stack[:,:,stack_idx] = pcv.rgb2gray(rgb_img=img)
            mask_stack[:,:,stack_idx] = mask
            markers[:,:,stack_idx] = out_labels[:,:,frame]
            stack_idx += 1

        # edges using 3D sobel operator as elevation map for watershed
        edges = ndi.generic_gradient_magnitude(img_stack, ndi.sobel)
        # segmentation using the watershed algorithm
        labels = watershed(edges, markers=markers, mask=mask_stack, compactness=0)
        out_labels[:,:,n] = labels[:,:,half_k]

        # Create images for plotting and printing (debug mode)
        rgb_seg = _labels2rgb(out_labels[:,:,n], n_labels, rgb_values)
        vis_seg = cv.addWeighted(img_n_rgb, 0.7, rgb_seg, 0.3, 0.0)
        params.debug = debug
        _debug(visual=vis_seg, filename=os.path.join(params.debug_outdir,
                                f"{str(params.device)}_{image_names[n][:-4]}_WSeg.png"))
        params.debug = None

    if save_labels == True:
        [np.save(os.path.join(params.debug_outdir, f"{image_names[i][:-4]}_labels"),
                out_labels[:,:,i]) for i in range(N)]

    return out_labels
