# from setuptools import setup, find_packages

from distutils.core import setup

import setuptools
import decaf_componentmanager

setup(
    name='decaf-componentmanager',
    version=decaf_componentmanager.__version__,
    packages=setuptools.find_packages(exclude=['tests']),
    url='http://decaf.example.net',
    license='',
    author='akrakau',
    author_email='akrakau@mail.upb.de',
    description='',
    test_suite='tests',
    zip_safe=False,
    entry_points={
      'console_scripts':[
          'componentmanagerd = decaf_componentmanager.componentmanagerd:daemon',
      ]
    },
    install_requires=[
        'SQLAlchemy>=0.9.8',
        'PyYAML>=3.11',
        'python-daemon>=2.0.6',
        'argcomplete>=1.0.0',
        'Twisted>=14.0.2',
        #'decaf-utils-rpc>=0.1'
    ],
)
