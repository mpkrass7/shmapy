import setuptools

__project__ = "shmapy"

if __name__ == "__main__":
    setuptools.setup(
        entry_points={
            "console_scripts": [f"{__project__} = {__project__}.__main__:main",]
        },
    )
