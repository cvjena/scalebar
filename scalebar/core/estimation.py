import cv2
import numpy as np
import typing as T

from scipy.spatial.distance import pdist
from skimage import feature

from scalebar.core.position import Position
from scalebar.utils import corner_ops


def get_scale(img: np.ndarray,
              pos: Position = Position.top_right,
              crop_size: float = 0.2,
              crop_square: bool = False,
              square_unit: float = 1.0,
              min_dist: int = 5,
              max_corners: int = np.inf,
              cv2_corners: bool = True,
              filter_corners: bool = False,
              rectify_corners: bool = False,
              binarize: bool = False,
              return_intermediate: bool = False) -> T.Optional[float]:
    """
        Estimates the scale from the image in pixel per mm

        Arguments:
            img: input image
            pos: position of the scale bar in the image
            square_unit: length of a single square in the scale bar in mm
            min_dist: minimum distance in pixel between two corners
            max_corners: maximum amount of corners that will be estimated
            cv2_corners: flag to use the cv2 implementation (if True)
                or the scikit-image implementation (if False, default)

        Returns:
            scale: scaling factor in pixel per mm
            intermediate: (optional) returns intermediate estimations
                as dictionary with following keys:
                    * detected_corners
                    * filter_mask
                    * rectification_angle
                    * final_corners
    """
    if isinstance(crop_size, float):
        crop_x = crop_y = crop_size
    elif isinstance(crop_size, (tuple, list)):
        crop_x, crop_y = crop_size
    else:
        raise ValueError(f"Unsupported crop size type: {crop_size=} (of type {type(crop_size).__name__})!")
    crop = pos.crop(img, x=crop_x, y=crop_y, square=crop_square)

    intermediate = dict(
        init_crop=crop,
        detected_corners=None,
        filter_mask=None,
        rectification_angle=None,
        final_corners=None,
    )

    crop = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)

    if binarize:
        blur = cv2.GaussianBlur(crop, (5,5),0)
        thresh, crop = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    intermediate["crop"] = crop

    if cv2_corners:
        # OpenCV's corner/feature detector
        corners = cv2.goodFeaturesToTrack(crop, 0 if np.isinf(max_corners) else max_corners, 0.5, min_dist)
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(crop, corners, (11,11), (-1,-1), criteria)
        # switch x and y coordinates for convenience (needed only for OpenCV)
        corners = corners[:, 0, ::-1].astype(int)
    else:
        # This is from Erik's code
        resp = feature.corner_shi_tomasi(crop)
        corners = feature.corner_peaks(resp,
                                       min_distance=min_dist,
                                       num_peaks=max_corners)
    if len(corners) == 0:
        if return_intermediate:
            return None, intermediate
        else:
            return None

    intermediate["detected_corners"] = corners

    if filter_corners:
        mask = corner_ops.filter(corners, crop)
    else:
        mask = np.ones(len(corners), dtype=bool)    

    intermediate["filter_mask"] = mask
    corners = corners[mask]

    if rectify_corners:
        corners, angle = corner_ops.rectify(corners)
    else:
        angle = 0.0

    intermediate["rectification_angle"] = angle
    intermediate["final_corners"] = corners

    distances = pdist(corners, metric="cityblock")
    if len(distances) != 0:
        # unit_distance is in "pixel per square-block"
        unit_distance = optimal_distance(distances)

        scale = unit_distance / square_unit
    
    else:
        scale = None

    if return_intermediate:
        return scale, intermediate
    else:
        return scale


def optimal_distance(distances: np.ndarray, step: float = 0.25) -> float:
    """
        Estimates the best distance by solving an
        optimization problem
    """

    smallest_err = np.inf
    best_distance = None
    max_d = np.percentile(distances, 20)
    min_d = max(1.0, np.percentile(distances, 1))

    for d in np.arange(min_d, max_d):
        grid = np.arange(0, np.max(distances) + d, d)
        if len(grid) <= 2:
            continue

        # compute quantization error
        bins = (grid[:-1] + grid[1:]) / 2.0
        prototypes = grid[1:-1]
        bin_idxs = np.digitize(distances, bins)
        bin_idxs -= 1
        bin_idxs[bin_idxs == -1] = 0
        bin_idxs[bin_idxs == len(prototypes)] = len(prototypes) - 1

        # quantization error with BIC model selection
        # adhoc version
        n = len(distances)
        err = np.linalg.norm(distances - prototypes[bin_idxs]) + \
            len(prototypes) * np.log(n)
        # theoretically derived criterion
        # err = n * np.log(2 * np.pi) + \
        #     np.linalg.norm(distances - prototypes[bin_idxs])**2 + \
        #     len(prototypes) * np.log(n)

        if err < smallest_err:
            smallest_err = err
            best_distance = d

    return best_distance
