import enum
import numpy as np


class Position(enum.Enum):
    none = enum.auto()
    top_right = enum.auto()
    bottom_right = enum.auto()
    top_left = enum.auto()
    bottom_left = enum.auto()

    def crop(self,
             img: np.ndarray,
             x: float = 0.2,
             y: float = 0.2,
             square: bool = True) -> np.ndarray:
        H, W, *C = img.shape
        if square:
            h = w = min(int(y * H), int(x * W))
        else:
            h, w = int(y * H), int(x * W)

        if self is Position.none:
            raise NotImplementedError("None is not implemented yet!")

        if self is Position.bottom_right:
            return img[-h:, -w:]

        if self is Position.top_right:
            return img[:h, -w:]

        if self is Position.bottom_left:
            return img[-h:, :w]

        if self is Position.top_left:
            return img[:h, :w]
