try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNaker_DataSpecification",
    version="0.1-SNAPSHOT",
    description="Specification of Memory Images",
    url="https://github.com/SpiNNakerManchester/DataSpecification",
    license="GNU GPLv3.0",
    packages=['data_specification',
              'data_specification.enums'],
    install_requires=['six', 'enum34']
)
