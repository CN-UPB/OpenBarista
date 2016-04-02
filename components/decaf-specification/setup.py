from distutils.core import setup
import setuptools
from decaf_specification import __version__

setup(
    name='decaf-specification',
    version=__version__,
    packages=setuptools.find_packages(exclude=['tests']),
    test_suite='tests',
    url='',
    license='',
    author='sergio',
    author_email='sergio@gmail.com',
    description='',
    entry_points={
      'console_scripts': [
          'specificationd = decaf_specification.specification:daemon',
      ]
    }
)
