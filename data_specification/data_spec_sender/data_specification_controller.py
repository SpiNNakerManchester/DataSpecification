from data_specification_sender import DataSpecificationSender
from file_data_reader import FileDataReader
from spec_sender import SpecSender

from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.transceiver import create_transceiver_from_hostname

filename = "/home/paul/spinn/application_generated_data_files/latest/192.168.240.253_dataSpec_0_0_2.dat"

fileReader = FileDataReader(filename)

#connection = UDPSpinnakerConnection(remote_host='192.168.240.253')

transceiver = create_transceiver_from_hostname('192.168.240.253', 3)

header     = SDPHeader(flags=SDPFlag.REPLY_NOT_EXPECTED, destination_cpu=2,
                       destination_chip_x=0, destination_chip_y=0,
                       destination_port=1)
sender     = SpecSender(transceiver, None)

dataSpecSender = DataSpecificationSender(fileReader, sender)
dataSpecSender.sendSpec()

