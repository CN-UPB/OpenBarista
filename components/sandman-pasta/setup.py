# from setuptools import setup, find_packages

from distutils.core import setup
from sandman_pasta import __version__
import setuptools

import decaf_cli

setup(
    name='sandman-pasta',
    version=__version__,
    packages=setuptools.find_packages(exclude=['tests']),
    url='http://fg-cn-sandman1.cs.uni-paderborn.de',
    license='',
    author='pg-sandman',
    author_email='',
    description='',
    test_suite='tests',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pastad = sandman_pasta:daemon',
        ]
    },
)
