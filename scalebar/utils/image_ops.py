import typing as T
import numpy as np

from pathlib import Path
from imageio import imread


def read_image(path: T.Optional[T.Union[str, Path]],
               mode: str = "RGB") -> np.ndarray:
    """
        Reads an image located at the given path
    """
    im = imread(path, pilmode=mode)

    return im
