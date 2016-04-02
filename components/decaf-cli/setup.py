# from setuptools import setup, find_packages

from distutils.core import setup

import setuptools

import decaf_cli

setup(
    name='decaf-cli',
    version=decaf_cli.__version__,
    packages=setuptools.find_packages(exclude=['tests']),
    url='http://decaf.example.net',
    license='',
    author='akrakau',
    author_email='akrakau@mail.upb.de',
    description='',
    test_suite='tests',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'decaf-cli = decaf_cli.cli:cli',
        ]
    },
)
