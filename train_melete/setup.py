"""
File primarily used to simulate venv building?
"""
print('hits setup pre import')
from setuptools import find_packages
from setuptools import setup
print('hits setup')

# This has to be for local packages, documentation says libraries installed on container level (which would make sense)
REQUIRED_PACKAGES = []

setup(
    name='melete_cloud_prototype',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='Melete Initial prototype'
)