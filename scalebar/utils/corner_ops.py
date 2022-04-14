import cv2
import numpy as np

import typing as T


def filter(points: np.ndarray,
           img: np.ndarray,
           window_size: int = 7) -> np.ndarray:
    """
        This filter checks the local pixel neighbourhood
        for the given window size and separates between
        corners with high and low intensity variance
        in these areas
    """
    size = (window_size - 1) // 2
    x0s = np.maximum(points[:, 1] - size, 0)
    y0s = np.maximum(points[:, 0] - size, 0)
    x1s = x0s + window_size
    y1s = y0s + window_size

    windows = [img[y0:y1, x0:x1] for x0, y0, x1, y1 in zip(x0s, y0s, x1s, y1s)]
    pixel_scaler = 255 if img.dtype == np.uint8 else 1
    windows = np.array(windows) / pixel_scaler

    win_var = windows.var(axis=(1, 2))
    mean_var = win_var.mean()
    return win_var >= mean_var


def rectify(points: np.ndarray) -> T.Tuple[np.ndarray, float]:
    """
        Rectify the points so that the dominant direction
        is paralell to the image axes.
    """

    angle = get_angle(points)

    # flip to the other image axis
    if abs(angle) >= 45:
        angle = np.sign(angle) * (np.abs(angle) - 90)

    rot_mat = cv2.getRotationMatrix2D([0, 0], -angle, 1.0)
    # homogeneous coordinates
    h_pts = np.hstack([points, np.ones((len(points), 1))])

    new_pts = np.round(h_pts @ rot_mat.T)
    return new_pts, angle


def get_angle(points: np.ndarray) -> float:
    """
        Estimates the dominant direction of a set of points
        by finding lines in these points.
        The slope of the line with the most votes
        is returned.
    """
    origin = points.min(axis=0)

    X = points - origin

    data = X.reshape(-1, 1, 2)[..., ::-1]
    kwargs = dict(lines_max=1,
                  threshold=1,
                  min_rho=0,
                  max_rho=360,
                  rho_step=1,
                  min_theta=0,
                  max_theta=np.pi,
                  theta_step=np.pi / 90)

    lines = cv2.HoughLinesPointSet(data, **kwargs)

    votes, r, phi = lines[0, 0]
    return phi / np.pi * 180
