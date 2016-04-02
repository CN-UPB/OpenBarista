# from setuptools import setup, find_packages

from distutils.core import setup

import setuptools

import decaf_deployment

setup(
    name='decaf-deployment',
    version=decaf_deployment.__version__,
    packages=setuptools.find_packages(exclude=['tests']),
    url='http://decaf.example.net',
    license='',
    author='tksarkar',
    author_email='tksarkar@mail.upb.de',
    description='',
    test_suite='tests',
    zip_safe=False,
    entry_points={
      'console_scripts': [
          'deploymentd = decaf_deployment.deployment:daemon',
      ]
    }
)
