# from setuptools import setup, find_packages

from distutils.core import setup

import setuptools

import example_scaling

setup(
    name='example_scaling',
    version=example_scaling.__version__,
    packages=setuptools.find_packages(exclude=['tests']),
    author='',
    url='',
    license='',
    description='An example of a scaling plugin',
    test_suite='tests',
    zip_safe=False,
    entry_points={
      'console_scripts': [
          'example_scalingd = example_scaling.example_scaling:daemon',
      ]
    },
)
