#!/usr/bin/env python
if __name__ != '__main__':
    raise Exception("Do not import me!")

import cv2
import scalebar

from scalebar import utils

with utils.try_import("cvargparse"):
    from cvargparse import Arg
    from cvargparse import BaseParser

with utils.try_import("matplotlib, pyqt5"):
    from matplotlib import pyplot as plt


def main(args) -> None:
    fig = plt.figure()

    im = utils.read_image(args.image_path)
    H, W, *C = im.shape

    grid = plt.GridSpec(3, 2)

    ax = plt.subplot(grid[:1, :])
    ax.axis("off")
    ax.imshow(im)
    ax.set_title("Input image")

    positions = {pos.name.lower(): pos for pos in scalebar.Position}
    pos = positions[args.position]
    crop = pos.crop(im)
    px_per_mm, interm = scalebar.get_scale(im,
                                           pos=pos,
                                           square_unit=args.unit,
                                           return_intermediate=True)

    init_corners = interm["detected_corners"]
    mask = interm["filter_mask"]
    angle = interm["rectification_angle"]
    corners = interm["final_corners"]

    ax = plt.subplot(grid[-2:, 0])
    ax.axis("off")
    ax.imshow(crop)
    ax.set_title("Original crop")

    ys, xs = init_corners[mask].transpose(1, 0)
    ax.scatter(xs, ys, marker=".", c="red", label="used")
    ys, xs = init_corners[~mask].transpose(1, 0)
    ax.scatter(xs, ys, marker=".", c="blue", alpha=0.7, label="rejected")
    ax.legend(loc="upper right")

    ax = plt.subplot(grid[-2:, 1])

    rot_mat = cv2.getRotationMatrix2D([0, 0], angle, 1.0)
    new_crop = cv2.warpAffine(crop, rot_mat, crop.shape[:2])

    ax.imshow(new_crop)
    ax.axis("off")
    ax.set_title("Rectified crop")
    ys, xs = corners.transpose(1, 0)
    ax.scatter(xs, ys, marker=".", c="red")

    if px_per_mm is None:
        fig.suptitle(f"Estimation Failed!")
    else:
        size = W / px_per_mm, H / px_per_mm
        fig.suptitle(" | ".join(
            [
                f"{px_per_mm:.2f} px/mm",
                f"Image size: {size[0]:.2f} x {size[1]:.2f}mm"
            ]))

    plt.tight_layout()
    plt.show()
    plt.close()


parser = BaseParser([
    Arg("image_path"),

    Arg("--position", "-pos", default="top_right",
        choices=[pos.name.lower() for pos in scalebar.Position]),

    Arg("--unit", "-u", type=float, default=1.0,
        help="Size of a single square in the scale bar (in mm). Default: 1"),
])
main(parser.parse_args())
