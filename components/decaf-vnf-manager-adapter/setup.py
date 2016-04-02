from distutils.core import setup
from setuptools import find_packages
import os
from decaf_vnf_manager_adapter import __version__

try:
    os.symlink('../res', 'decaf_vnf_manager_adapter/res')
    setup(
        name='decaf-vnf-manager-adapter',
        version=__version__,
        packages=find_packages(exclude=['test*']),
        test_suite='test',
        url='',
        license='',
        author='thgoette',
        author_email='thgoette@mail.upb.de',
        package_data={'': ['res/*.py', 'res/*.sh']},
        #include_package_data=True,
        description='An adapter plugin that creates generic VNFMangers',
        zip_safe=False,
        entry_points={
          'console_scripts': [
              'vnf_manager_adapterd = decaf_vnf_manager_adapter.decaf_vnf_manager_adapter:daemon'
          ]
        }
    )
finally:
    os.unlink('decaf_vnf_manager_adapter/res')
