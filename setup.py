from setuptools import setup, find_packages
import sys, os

version = '1.0'
setup(
    name = 'trackingshell',
    version = version,
    description = "Tracks makefiles targets.",
    packages = find_packages( exclude = [ 'ez_setup'] ),
    include_package_data = True,
    zip_safe = False,
    author = 'Torsten Becker, Bence Faludi',
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