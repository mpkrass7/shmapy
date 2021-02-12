from distutils.core import setup
from lone_wolf import __project__

setup(
    name="lone_wolf",
    version="0.1dev",
    packages=[
        "lone_wolf",
    ],
    license="Creative Commons Attribution-Noncommercial-Share Alike license",
    long_description=open("README.md").read(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            f"{__project__} = {__project__}.__main__:main",
        ]
    },
)
