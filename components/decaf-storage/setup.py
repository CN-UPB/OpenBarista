from distutils.core import setup
import setuptools
import decaf_storage

"""

To setup PostgreSQL and DB driver run the following

    $ apt-get install postgresql
    $ apt-get install postgresql-contrib
    $ apt-get install python-dev
    $ apt-get install postgresql-server-dev-a.b
    $ sudo pip install psycopg2
    $ sudo pip install sqlalchemy
    create db for component:
    $ sudo su - postgres
    $ psql
    $# CREATE USER pgdecaf WITH PASSWORD 'pgdecafpw';
    $# CREATE DATABASE decaf_storage OWNER pgdecaf;
    $# \c <dbname>
    enable uuid extension for new db:
    $# CREATE EXTENSION "uuid-ossp";
    create DB tables from within deamon start.

"""
setup(
    name='decaf-storage',
    version=decaf_storage.__version__,
    packages=setuptools.find_packages(exclude=['tests']),
    test_suite='tests',
    url='',
    license='',
    author='',
    author_email='',
    description='',
    entry_points={
      'console_scripts': [
          'storaged = decaf_storage.storage:daemon',
      ]
    },
)
