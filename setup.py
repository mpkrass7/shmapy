import os

from codecs import open as copen
from setuptools import setup
from shmapy import __project__

here = os.path.abspath(os.path.dirname(__file__))

# get the dependencies and installs
with copen(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")

install_requires = [x.strip() for x in all_reqs if "git+" not in x]

setup(
    name="lone_wolf",
    version="0.1",
    packages=[
        "lone_wolf",
    ],
    license="Creative Commons Attribution-Noncommercial-Share Alike license",
    long_description=open("README.md").read(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            f"{__project__} = {__project__}.__main__:main",
        ]
    },
)
