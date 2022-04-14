import contextlib

from scalebar.utils.image_ops import read_image
from scalebar.utils.corner_ops import rectify
from scalebar.utils.corner_ops import filter as filter_corners


@contextlib.contextmanager
def try_import(package_name):
    try:
        yield
    except ImportError:
        msg = f"{package_name} not found! " + \
            f"Install it with 'pip install {package_name}'!"
        print(msg)
        raise


__all__ = [
    "try_import",
    "read_image",
    "rectify",
    "filter_corners",
]
