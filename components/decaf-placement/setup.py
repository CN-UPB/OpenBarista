from distutils.core import setup

import setuptools

import decaf_placement

setup(
    name='decaf-placement',
    version=decaf_placement.__version__,
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
          'placementd = decaf_placement.placement:daemon',
      ]
    }
)
