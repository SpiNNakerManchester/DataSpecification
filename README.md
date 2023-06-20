This repository is no longer being used

All code that was used has been moved to https://github.com/SpiNNakerManchester/SpiNNFrontEndCommon/tree/master/spinn_front_end_common/interface/ds

Please replace

from data_specification.enums import DataType

with

from spinn_front_end_common.interface.ds import DataType

DataSpecificationException is never throw any more so any checks for that can be safely removed

