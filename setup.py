#!/usr/bin/env python
from pathlib import Path

from setuptools import find_packages
from setuptools import setup

pkg_name = "scalebar"

cwd = Path(__file__).parent.resolve()

# Get __version__ variable
__version__ = None
exec(open(str(cwd / pkg_name / '_version.py')).read())

with open(str(cwd / "requirements.txt")) as f:
    install_requires = [line.strip() for line in f]

setup(
    name=pkg_name,
    version=__version__,
    description='Processing tools for scale bars in images.',
    author='Dimitri Korsch',
    author_email='korschdima@gmail.com',
    license='AGPL-3.0 License',
    packages=find_packages(),
    zip_safe=False,
    setup_requires=[],
    install_requires=install_requires,
    package_data={'': ['requirements.txt']},
    data_files=[('.', ['requirements.txt'])],
    include_package_data=True,
)
