#!/usr/bin/env python
if __name__ != '__main__':
    raise Exception("Do not import me!")

import os
import scalebar

from scalebar import utils

with utils.try_import("cvargparse"):
    from cvargparse import Arg
    from cvargparse import BaseParser


def main(args):

    im = utils.read_image(args.image_path)

    positions = {pos.name.lower(): pos for pos in scalebar.Position}
    pos = positions[args.position]
    px_per_mm = scalebar.get_scale(im,
                                   pos=pos,
                                   square_unit=args.unit)

    if args.output:
        assert not os.path.exists(args.output), \
            f"Output file ({args.output}) already exists!"
        with open(args.output, "w") as f:
            f.write(f"{px_per_mm:f}\n")
    else:
        print(px_per_mm)


parser = BaseParser([
    Arg("image_path"),

    Arg("--position", "-pos", default="top_right",
        choices=[pos.name.lower() for pos in scalebar.Position]),

    Arg("--unit", "-u", type=float, default=1.0,
        help="Size of a single square in the scale bar (in mm). Default: 1"),

    Arg("--output", "-o")
])

main(parser.parse_args())
