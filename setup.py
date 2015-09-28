from setuptools import setup, find_packages
import sys, os

version = '1.0.1'
setup(
    name = 'trackingshell',
    version = version,
    description = "You can track the target execution of a makefile with this tool easily.",
    packages = find_packages( exclude = [ 'ez_setup'] ),
    include_package_data = True,
    zip_safe = False,
    author = 'Bence Faludi, Torsten Becker',
    author_email = 'befaludi@microsoft.com',
    license = 'MIT',
    install_requires = [],
    test_suite = "trackingshell.tests",
    entry_points = {
        'console_scripts': [
            'trackingshell = trackingshell:main',
        ],
    },
    url = 'http://6wunderkinder.com'
)