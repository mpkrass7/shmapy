from distutils.core import setup

setup(
    name='Lone_wolf',
    version='0.1dev',
    packages=['lone_wolf',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    include_package_data=True,
    entry_points={
    'console_scripts': [
        f'{__project__} = {__project__}.__main__:main',
    ]
},
)
