try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNaker_DataSpecification",
    version="2016.001",
    description="Specification of Memory Images",
    url="https://github.com/SpiNNakerManchester/DataSpecification",
    license="GNU GPLv3.0",
    packages=['data_specification',
              'data_specification.data_spec_sender',
              'data_specification.enums'],
    package_data={'data_specification.data_spec_sender': ['*.aplx']},
    install_requires=['SpiNNStorageHandlers >= 2016.001',
                      'six', 'enum34']
)
