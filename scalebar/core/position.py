from __future__ import annotations

import enum
import numpy as np

from scalebar import utils

class Position(enum.Enum):
    # none = enum.auto()
    top_right = enum.auto()
    bottom_right = enum.auto()
    top_left = enum.auto()
    bottom_left = enum.auto()

    # these are always in the middle
    top = enum.auto()
    bottom = enum.auto()
    left = enum.auto()
    right = enum.auto()

    def crop(self,
             img: np.ndarray,
             x: float = 0.2,
             y: float = 0.2,
             square: bool = True) -> np.ndarray:
        H, W, *C = img.shape
        cy, cx = H//2, W//2

        if square:
            h = w = min(int(y * H), int(x * W))
        else:
            h, w = int(y * H), int(x * W)

        if self is Position.bottom_right:
            return img[-h:, -w:]

        if self is Position.top_right:
            return img[:h, -w:]

        if self is Position.bottom_left:
            return img[-h:, :w]

        if self is Position.top_left:
            return img[:h, :w]
        
        if self is Position.top:
            return img[:h, max(cx-w//2, 0):cx+w//2]
        
        if self is Position.bottom:
            return img[-h:, max(cx-w//2, 0):cx+w//2]
        
        if self is Position.left:
            return img[max(cy-h//2,0):cy+h//2, :w]
        
        if self is Position.right:
            return img[max(cy-h//2,0):cy+h//2, -w:]

        raise NotImplementedError("None is not implemented yet!")

    @staticmethod
    def estimate(img, *, fraction: float = 0.3) -> Position:
        size = int(min(img.shape[:2]) / 10 * fraction)
        hsize = size // 2
        pattern = utils.create_pattern(2, 10, size=size)
        
        bkg = np.zeros_like(img, dtype=np.float32)

        for pat in [pattern, pattern.T]:
            kpts = utils.match_pattern(img, pat, dist_thresh=0.75)
            for x, y in kpts:
                x0, y0 = max(int(x)-hsize, 0), max(int(y)-hsize, 0)
                x1, y1 = x0 + size, y0 + size
                bkg[y0:y1, x0:x1] += 1.0
        
        pos_values = [(pos, pos.crop(bkg, x=fraction, y=fraction, square=False).sum()) for pos in Position]
        # for pos, val in pos_values:
        #     print(pos, val)

        return max(pos_values, key=lambda el: el[1])[0]