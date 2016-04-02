from distutils.core import setup
import setuptools
from decaf_masta import __version__

setup(
    name='decaf-masta',
    version=__version__,
    packages=setuptools.find_packages(exclude=['tests']),
    test_suite='tests',
    url='',
    license='',
    author='krijan',
    author_email='kristiwn@gmail.com',
    description='',
    entry_points={
      'console_scripts': [
          'mastad = decaf_masta.masta:daemon'
      ]
    }
)
