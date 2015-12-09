try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNaker_DataSpecification",
    version="2015.004",
    description="Specification of Memory Images",
    url="https://github.com/SpiNNakerManchester/DataSpecification",
    license="GNU GPLv3.0",
    packages=['data_specification',
              'data_specification.enums'],
    install_requires=['SpiNNStorageHandlers >= 2016.001.01',
                      'six', 'enum34']
)
