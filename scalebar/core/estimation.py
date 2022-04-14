import cv2
import numpy as np
import typing as T

from scipy.spatial.distance import pdist
from skimage import feature

from scalebar.core.position import Position
from scalebar.utils import corner_ops


def get_scale(img: np.ndarray,
              pos: Position = Position.top_right,
              square_unit: float = 1.0,
              min_dist: int = 5,
              max_corners: int = 200,
              cv2_corners: bool = False,
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

    crop = pos.crop(img, x=0.2, y=0.2)
    crop = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    intermediate = dict(
        detected_corners=None,
        filter_mask=None,
        rectification_angle=None,
        final_corners=None,
    )

    if cv2_corners:
        # OpenCV's corner/feature detector
        corners = cv2.goodFeaturesToTrack(crop, max_corners, 0.5, min_dist)
        # switch x and y coordinates for convenience (needed only for OpenCV)
        corners = corners.squeeze()[:, ::-1]
    else:
        # This is from Erik's code
        resp = feature.corner_shi_tomasi(crop)
        corners = feature.corner_peaks(resp,
                                       min_distance=min_dist,
                                       num_peaks=max_corners)
    if len(corners) == 0:
        return None

    intermediate["detected_corners"] = corners

    mask = corner_ops.filter(corners, crop)
    intermediate["filter_mask"] = mask
    corners = corners[mask]
    corners, angle = corner_ops.rectify(corners)
    intermediate["rectification_angle"] = angle
    intermediate["final_corners"] = corners

    distances = pdist(corners, metric="cityblock")
    # unit_distance is in "pixel per square-block"
    unit_distance = optimal_distance(distances)

    scale = unit_distance / square_unit

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
    min_d = np.percentile(distances, 1)

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
