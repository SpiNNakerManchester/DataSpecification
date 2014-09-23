try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="DataSpecification",
    version="0.1-SNAPSHOT",
    description="Specification of Memory Images",
    url="https://github.com/SpiNNakerManchester/DataSpecification",
    packages=['data_specification',
              'data_specification.enums'],
    install_requires=['six', 'enum34']
)
