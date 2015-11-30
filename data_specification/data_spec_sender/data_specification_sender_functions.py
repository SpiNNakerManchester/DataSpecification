import struct
import constants
from command import Command


class DataSpecificationSenderFunctions:

    def __init__(self, spec_reader, spec_sender):
        self.spec_reader = spec_reader
        self.spec_sender = spec_sender

    def send_break(self, cmd):
        # print "Sending break"
        self.spec_sender.add(cmd.get_value())

    def send_nop(self, cmd):
        # print "Sending nop"
        self.spec_sender.add(cmd.get_value())

    def send_reserve(self, cmd):
        # print "Sending reserve"
        self.spec_sender.add(cmd.get_value())
        self.spec_sender.add(self.spec_reader.read(4))

    def send_write(self, cmd):
        # print "Sending write"

        self.spec_sender.add(cmd.get_value())
        for count in range(cmd.get_length()):
            self.spec_sender.add(self.spec_reader.read(4))

    def send_write_array(self, cmd):
        # print "Sending write array"

        self.spec_sender.add(cmd.get_value())

        length_encoded = self.spec_reader.read(4)
        self.spec_sender.add(length_encoded)

        length = struct.unpack("<I", str(length_encoded))[0]

        for i in xrange(length):
            value_encoded = self.spec_reader.read(4)
            self.spec_sender.add(value_encoded)

    def send_switch_focus(self, cmd):
        # print "Sending switch focus"
        self.spec_sender.add(cmd.get_value())

    def send_end_spec(self, cmd):
        # print "Sending end spec"
        self.spec_sender.add(cmd.get_value())
        return constants.END_SPEC_SENDER

    def send_loop(self, cmd):
        self.spec_sender.add(cmd.get_value())
        while cmd.get_opcode() != Commands.END_LOOP:
            cmd = Command(self.spec_reader.read(4))
            self.spec_sender.add(cmd.get_value())




