import struct
import constants

class DataSpecificationSenderFunctions:

    def __init__(self, spec_reader, spec_sender):
        self.spec_reader = spec_reader
        self.spec_sender = spec_sender

    def __unpack_cmd__(self, cmd):
        self._cmd_size = (cmd >> 28) & 0x3
        self.opcode = (cmd >> 20) & 0xFF
        self.use_dest_reg = (cmd >> 18) & 0x1 == 0x1
        self.use_src1_reg = (cmd >> 17) & 0x1 == 0x1
        self.use_src2_reg = (cmd >> 16) & 0x1 == 0x1
        self.dest_reg = (cmd >> 12) & 0xF
        self.src1_reg = (cmd >> 8) & 0xF
        self.src2_reg = (cmd >> 4) & 0xF
        self.data_len = (cmd >> 12) & 0x3

    def send_break(self, cmd):
        #print "Sending break"
        self.spec_sender.add(cmd)

    def send_nop(self, cmd):
        #print "Sending nop"
        self.spec_sender.add(cmd)

    def send_reserve(self, cmd):
        #print "Sending reserve"
        self.spec_sender.add(cmd)
        self.spec_sender.add(self.spec_reader.read(4))

    def send_write(self, cmd):
        #print "Sending write"
        self.__unpack_cmd__(cmd)

        self.spec_sender.add(cmd)
        for count in range(self.data_len - 1):
            self.spec_sender.add(self.spec_reader.read(4))

    def send_write_array(self, cmd):
        #print "Sending write array"

        self.spec_sender.add(cmd)

        length_encoded = self.spec_reader.read(4)
        self.spec_sender.add(length_encoded)

        length = struct.unpack("<I", str(length_encoded))[0]

        for i in xrange(length):
            value_encoded = self.spec_reader.read(4)
            self.spec_sender.add(value_encoded)

    def send_switch_focus(self, cmd):
        #print "Sending switch focus"
        self.__unpack_cmd__(cmd)
        self.spec_sender.add(cmd)

    def send_end_spec(self, cmd):
        #print "Sending end spec"
        read_data = self.spec_reader.read(4)
        self.spec_sender.add(cmd)
        return constants.END_SPEC_SENDER
