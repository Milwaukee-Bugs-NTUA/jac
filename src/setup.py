from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'J.A.C.: Just Another Chord Implementation'
LONG_DESCRIPTION = 'A simpler implementation of Chord, a scalable P2P lookup service for internet applications.'
AUTHORS = 'Giannis Fakinos, Panagiotis Kranias'

# Setting up
setup(
        name="jacmodule", 
        version=VERSION,
        author=AUTHORS,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license='MIT',
        url='https://https://github.com/Milwaukee-Bugs-NTUA/jac',
        packages=find_packages(),
        install_requires=[
            "click",
            "cmd2",
            "requests",
            "pyfiglet",
            "Flask",
            "prettytable",
        ],
)