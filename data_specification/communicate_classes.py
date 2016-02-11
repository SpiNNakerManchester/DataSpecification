#Transceiver and SDP Messages
import traceback

import spinnman.transceiver as transceiver
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.sdp.sdp_message import SDPMessage
#EIEIO generic fields
from spinnman.messages.eieio.eieio_type import EIEIOType
from spinnman.messages.eieio.eieio_prefix  import EIEIOPrefix
#EIEIO Command specific
from spinnman.messages.eieio.command_messages.eieio_command_header import EIEIOCommandHeader
from spinnman.messages.eieio.command_messages.eieio_command_message import EIEIOCommandMessage

from spinnman.messages.eieio.command_messages.spinnaker_request_buffers import SpinnakerRequestBuffers
from spinnman.messages.eieio.command_messages.host_send_sequenced_data import HostSendSequencedData
from spinnman.messages.eieio.command_messages.event_stop_request import EventStopRequest
from spinnman.messages.eieio.data_messages.eieio_data_message import EIEIODataHeader
from spinnman.messages.eieio.data_messages.eieio_data_message import EIEIODataMessage

#UDP server
from spinnman.connections.udp_packet_connections.udp_connection import UDPConnection
from spinnman.connections.abstract_classes.abstract_listenable import AbstractListenable

#struct python library
import struct
import time
import threading

class DataSpecMessage():
    """

    Definition of the message for data spec
    data composed by multiple chunks made of

    flags | length | value          <--- chunk
      1 B |  1 B   | up to 252      <--- size

    """

    def __init__(self, data=b'', len = 0):

        self._len = len
        self.data=data
        self.fragmented_flag=0


    def addFormattedCommand(self, cmd_word, is_fragmented=False, is_last_frag=False, is_first_frag=False):

        #first of all check the command length is valid for the current message
        com_len=len(cmd_word)
        if((com_len+self._len+2) >205): #two are the bytes needed for the flag/length "header" of the command chunk
            return -1
        frag_flag=0;
        #if the length is ok set the flags and add the content
        if(is_fragmented):
            if(is_last_frag):
                frag_flag=3
            else:
                if is_first_frag:
                    frag_flag=2
                else:
                    frag_flag=1

        self.data+=struct.pack("<B", frag_flag)+struct.pack("<B", com_len)+cmd_word;
        self._len+=(com_len+2)

        return 1

    def addIpTag(self, iptag_value):
        self.data=iptag_value

    def add_row_initial_values(self, values):
        self.data=values

    def addIpTagToFormat(self, iptag_integer):
        self.data=struct.pack("<H", iptag_integer);

    def clean(self):
        self._len=0
        self.data=b''
        self.fragmented_flag=0

    @property
    def bytestring(self):
        #return struct.pack("<B", self.fragmented_flag)+struct.pack("<B", self._len)+self.data
        return self.data



class DataSpecRemoteWriter():

    def __init__(self, transceiver):
        self.communicators=dict()
        self.transceiver=transceiver

    def addCommunicator(self, x, y, p, iptag):
        self.communicators[str(x)+str(y)+str(p)]=CorePacketListCreator(self.transceiver, x, y, p, iptag)

    def writeCommand(self, x, y, p, command):
        self.communicators[str(x)+str(y)+str(p)].writeCommand(command);

    def resendPacketFrom(self, x, y, p, lastseen):
        self.communicators[str(x)+str(y)+str(p)].resendFrom(lastseen)

'''
class CorePacketListCreatorAsyncSend():

    ENCODED_DELIMITERS = bytearray(struct.pack("<I", ((0x00 << 28) | (0XFF << 20)))) + struct.pack("<i", -1)

    def __init__(self, x, y, p, iptag, future_id=0, report_flag=0, queue=None):
        self.x = x
        self.y = y
        self.p = p
        self.header = SDPHeader(flags=SDPFlag.REPLY_NOT_EXPECTED,
                              destination_cpu=self.p,
                              destination_chip_x=self.x,
                              destination_chip_y=self.y,
                              destination_port=1)
        self.queue = queue
        self.counter = 0
        self.stored_packets = list()
        self.iptag=iptag
        self.lastpacket = DataSpecMessage()
        self.future_id=future_id
        self.report_flag=report_flag
        self.transceiver = transceiver
        self.commands=list()
        self.addIpTag()
        self.was_last_stored=False
        self.monitor = threading.Lock() #it allows to make "atomic" the sending operations and the access to counter

    def addIpTag(self):
        datatoadd=struct.pack("<H", self.iptag)+struct.pack("<H", self.future_id)+struct.pack("<H", self.report_flag)
        self.lastpacket.add_row_initial_values(datatoadd)
        r=HostSendSequencedData(region_id=1, sequence_no=0, eieio_data_message=self.lastpacket)
        self.stored_packets.append(r)

        self.queue.put([self.header, r.bytestring])

        self.lastpacket=DataSpecMessage()
        self.incrementCounter()

    def get_packets_raw(self):
        newlist = list()
        for i in self.stored_packets:
            newlist.appen(i)
        return newlist

    def get_commands(self):
        return self.commands

    def writeCommand(self, cmdW, isthelast=False):
        #TODO IMPLEMENT mechanism to avoid to send more packets if there is a packet resend request (two different queues?)
        #TODO REVIEW of fragmentation management
        self.commands.append(cmdW)
        with self.monitor: #acquire lock
            if( len(cmdW) > 200 ): #split it and send each subpacket
                #flush out the last packet if was still not sent
                if( (self.was_last_stored==False) and (self.lastpacket._len!=0)):
                    self.store_last_packet()
                complete_pkts_to_do=int(len(cmdW)/200) #calc how many complete packets you have to do
                last_packet_len=(len(cmdW)%200) #calc the size of the last packet
                m = 200
                for i in range(0, complete_pkts_to_do): #iterate the number of complete packets
                    self.lastpacket = DataSpecMessage()
                    if(i is 0):
                        self.lastpacket.addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True, is_first_frag=True)
                    else:
                        if(i==(complete_pkts_to_do-1) and (last_packet_len is 0)): #is a multiple last packet
                            self.lastpacket.addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True, is_last_frag=True)
                        else: #normal packet
                            self.lastpacket.addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True)
                    self.store_last_packet()
                    self.was_last_stored = True
                if last_packet_len is not 0: #last packet
                    self.lastpacket = DataSpecMessage()
                    self.lastpacket.addFormattedCommand(cmdW[-last_packet_len:], is_fragmented=True, is_last_frag=True)
                    self.store_last_packet()
                    self.was_last_stored = True
            else:
                #if many commands can be added put them in the same packet,
                # if you reach the measure limit (addFormattedCommand returns -1)
                # send the packet and add the current command (rejected from the other) to the next
                # or if you have to write the last sequence (isthelast=True) write and send it
                if(self.lastpacket.addFormattedCommand(cmdW)<0): #if add to current fails
                    #too big for this packet send the last one (if was not sent yet)
                    if(self.was_last_stored==False and self.lastpacket._len!=0):
                       self.store_last_packet()
                       self.was_last_stored=True
                    #and create a new one
                    self.lastpacket=DataSpecMessage()
                    self.lastpacket.addFormattedCommand(cmdW)
                    if(cmdW == self.ENCODED_DELIMITERS): #force to send the last packet
                        #case final command that not fitted in the packet
                        self.store_last_packet(region=3)
                        self.was_last_stored=True
                        return
                    self.was_last_stored=False
                else:
                    #if is the last command write it and send the whole last packet
                    if(cmdW == self.ENCODED_DELIMITERS):
                        #case final command that fitted in the last packet
                        self.store_last_packet(region=3)
                        self.was_last_stored=True
                    else: #if it is not the last packet and the add did not fail set that was not sent yet
                        self.was_last_stored=False
        #automatically release the condition (out of indent)

    def store_last_packet(self, region=0):
        r=HostSendSequencedData(region_id=region, sequence_no=(self.counter % 256), eieio_data_message=self.lastpacket)
        self.stored_packets.append(r)
        self.queue.put([self.header, r.bytestring])
        self.lastpacket=DataSpecMessage() #once sent create one new
        self.incrementCounter()

    def reset_counter_to(self, lastseen):
        self.counter=lastseen

    def incrementCounter(self):
        self.counter+=1;
'''



class CorePacketListCreatorAsyncSend():


    def __init__(self, x, y, p, iptag, future_id=0, report_flag=0, queue=None, transceiver=None):

        from multiprocessing import Process, Queue

        self.x = x
        self.y = y
        self.p = p
        self.header = SDPHeader(flags=SDPFlag.REPLY_NOT_EXPECTED,
                              destination_cpu=self.p,
                              destination_chip_x=self.x,
                              destination_chip_y=self.y,
                              destination_port=1)
        self.queue = queue
        self.counter = 0
        self.stored_packets = list()
        self.iptag=iptag
        self.lastpacket = DataSpecMessage()
        self.future_id=future_id
        self.report_flag=report_flag
        self.transceiver = transceiver
        self.private_queue=Queue()
        self.p=Process(target=self.process_work, args=(self.header, self.iptag, self.future_id, self.report_flag, queue, self.private_queue, ))
        self.p.start()
        self.was_last_stored=False
        #self.monitor = threading.Lock() #it allows to make "atomic" the sending operations and the access to counter


    @staticmethod
    def process_work(header, iptag, future_id, report_flag, queue1, queue2):
        ENCODED_DELIMITERS = bytearray(struct.pack("<I", ((0x00 << 28) | (0XFF << 20)))) + struct.pack("<i", -1)
        lastpacket = DataSpecMessage()
        datatoadd=struct.pack("<H", iptag)+struct.pack("<H", future_id)+struct.pack("<H", report_flag)
        lastpacket.add_row_initial_values(datatoadd)
        r=HostSendSequencedData(region_id=1, sequence_no=0, eieio_data_message=lastpacket)
        queue1.put([header, r.bytestring])
        was_last_stored=True
        lastpacket.clean()
        region=0
        counter=1
        while True:
            cmdW=queue2.get()
            if( len(cmdW) > 200 ): #split it and send each subpacket
                #flush out the last packet if was still not sent
                if( (was_last_stored==False) and (lastpacket._len!=0)):
                    r=HostSendSequencedData(region_id=region, sequence_no=(counter % 256), eieio_data_message=lastpacket)
                    queue1.put([header, r.bytestring])
                    lastpacket.clean() #once sent create one new
                    counter+=1
                complete_pkts_to_do=int(len(cmdW)/200) #calc how many complete packets you have to do
                last_packet_len=(len(cmdW)%200) #calc the size of the last packet
                m = 200
                for i in range(0, complete_pkts_to_do): #iterate the number of complete packets
                    #lastpacket.clean()
                    if(i is 0):
                        lastpacket.addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True, is_first_frag=True)
                    else:
                        if(i==(complete_pkts_to_do-1) and (last_packet_len is 0)): #is a multiple last packet
                            lastpacket.addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True, is_last_frag=True)
                        else: #normal packet
                            lastpacket.addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True)
                    r=HostSendSequencedData(region_id=region, sequence_no=(counter % 256), eieio_data_message=lastpacket)
                    queue1.put([header, r.bytestring])
                    lastpacket.clean() #once sent create one new
                    counter+=1
                    was_last_stored = True
                if last_packet_len is not 0: #last packet
                    #lastpacket = DataSpecMessage()
                    lastpacket.addFormattedCommand(cmdW[-last_packet_len:], is_fragmented=True, is_last_frag=True)
                    r=HostSendSequencedData(region_id=region, sequence_no=(counter % 256), eieio_data_message=lastpacket)
                    queue1.put([header, r.bytestring])
                    lastpacket.clean() #once sent create one new
                    counter+=1
                    was_last_stored = True
            else:
                #if many commands can be added put them in the same packet,
                # if you reach the measure limit (addFormattedCommand returns -1)
                # send the packet and add the current command (rejected from the other) to the next
                # or if you have to write the last sequence (isthelast=True) write and send it
                if(lastpacket.addFormattedCommand(cmdW)<0): #if add to current fails
                    #too big for this packet send the last one (if was not sent yet)
                    if(was_last_stored==False and lastpacket._len!=0):
                        r=HostSendSequencedData(region_id=region, sequence_no=(counter % 256), eieio_data_message=lastpacket)
                        queue1.put([header, r.bytestring])
                        #lastpacket.clean() #once sent create one new
                        counter+=1
                        was_last_stored=True
                    #and create a new one
                    lastpacket.clean()
                    lastpacket.addFormattedCommand(cmdW)
                    if(cmdW == ENCODED_DELIMITERS): #force to send the last packet
                        #case final command that not fitted in the packet
                        r=HostSendSequencedData(region_id=3, sequence_no=(counter % 256), eieio_data_message=lastpacket)
                        queue1.put([header, r.bytestring])
                        #lastpacket.clean() #once sent create one new
                        counter+=1
                        was_last_stored=True
                        break
                    was_last_stored=False
                else:
                    #if is the last command write it and send the whole last packet
                    if(cmdW == ENCODED_DELIMITERS):
                        #case final command that fitted in the last packet
                        r=HostSendSequencedData(region_id=3, sequence_no=(counter % 256), eieio_data_message=lastpacket)
                        queue1.put([header, r.bytestring])
                        #lastpacket.clean() #once sent create one new
                        counter+=1
                        was_last_stored=True
                        break
                    else: #if it is not the last packet and the add did not fail set that was not sent yet
                        was_last_stored=False


    def get_packets_raw(self):
        newlist = list()
        for i in self.stored_packets:
            newlist.appen(i)
        return newlist

    def get_commands(self):
        return self.commands

    def writeCommand(self, cmdW, isthelast=False):
        self.private_queue.put(cmdW)

    def reset_counter_to(self, lastseen):
        self.counter=lastseen

    def incrementCounter(self):
        self.counter+=1;


class CorePacketListCreator():

    ENCODED_DELIMITERS = bytearray(struct.pack("<I", ((0x00 << 28) | (0XFF << 20)))) + struct.pack("<i", -1)

    def __init__(self, x, y, p, iptag, future_id=0, report_flag=0, send_now=False):
        self.x = x
        self.y = y
        self.p = p
        self.header = SDPHeader(flags=SDPFlag.REPLY_NOT_EXPECTED,
                              destination_cpu=self.p,
                              destination_chip_x=self.x,
                              destination_chip_y=self.y,
                              destination_port=1)
        self.counter = 0
        self.stored_packets = list()
        self.iptag=iptag
        self.lastpacket = DataSpecMessage()
        self.future_id=future_id
        self.report_flag=report_flag

        self.send_now = send_now
        self.transceiver = transceiver

        self.addIpTag()
        self.was_last_stored=False
        self.monitor = threading.Lock() #it allows to make "atomic" the sending operations and the access to counter

    def addIpTag(self):
        datatoadd=struct.pack("<H", self.iptag)+struct.pack("<H", self.future_id)+struct.pack("<H", self.report_flag)
        self.lastpacket.add_row_initial_values(datatoadd)
        r=HostSendSequencedData(region_id=1, sequence_no=0, eieio_data_message=self.lastpacket)
        self.stored_packets.append(r)
        self.lastpacket=DataSpecMessage()
        self.incrementCounter()

    def writeCommand(self, cmdW, isthelast=False):
        #TODO IMPLEMENT mechanism to avoid to send more packets if there is a packet resend request (two different queues?)
        #TODO REVIEW of fragmentation management

        with self.monitor: #acquire lock
            if( len(cmdW) > 200 ): #split it and send each subpacket
                #flush out the last packet if was still not sent
                if( (self.was_last_stored==False) and (self.lastpacket._len!=0)):
                    self.store_last_packet()
                complete_pkts_to_do=int(len(cmdW)/200) #calc how many complete packets you have to do
                last_packet_len=(len(cmdW)%200) #calc the size of the last packet
                m = 200
                for i in range(0, complete_pkts_to_do): #iterate the number of complete packets
                    self.lastpacket = DataSpecMessage()
                    if(i is 0):
                        self.lastpacket.addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True, is_first_frag=True)
                    else:
                        if(i==(complete_pkts_to_do-1) and (last_packet_len is 0)): #is a multiple last packet
                            self.lastpacket.addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True, is_last_frag=True)
                        else: #normal packet
                            self.lastpacket.addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True)
                    self.store_last_packet()
                    self.was_last_stored = True
                if last_packet_len is not 0: #last packet
                    self.lastpacket = DataSpecMessage()
                    self.lastpacket.addFormattedCommand(cmdW[-last_packet_len:], is_fragmented=True, is_last_frag=True)
                    self.store_last_packet()
                    self.was_last_stored = True
            else:
                #if many commands can be added put them in the same packet,
                # if you reach the measure limit (addFormattedCommand returns -1)
                # send the packet and add the current command (rejected from the other) to the next
                # or if you have to write the last sequence (isthelast=True) write and send it
                if(self.lastpacket.addFormattedCommand(cmdW)<0): #if add to current fails
                    #too big for this packet send the last one (if was not sent yet)
                    if(self.was_last_stored==False and self.lastpacket._len!=0):
                       self.store_last_packet()
                       self.was_last_stored=True
                    #and create a new one
                    self.lastpacket=DataSpecMessage()
                    self.lastpacket.addFormattedCommand(cmdW)
                    if(cmdW == self.ENCODED_DELIMITERS): #force to send the last packet
                        #case final command that not fitted in the packet
                        self.store_last_packet(region=3)
                        self.was_last_stored=True
                        return
                    self.was_last_stored=False
                else:
                    #if is the last command write it and send the whole last packet
                    if(cmdW == self.ENCODED_DELIMITERS):
                        #case final command that fitted in the last packet
                        self.store_last_packet(region=3)
                        self.was_last_stored=True
                    else: #if it is not the last packet and the add did not fail set that was not sent yet
                        self.was_last_stored=False
        #automatically release the condition (out of indent)

    def store_last_packet(self, region=0):
        r=HostSendSequencedData(region_id=region, sequence_no=(self.counter % 256), eieio_data_message=self.lastpacket)
        self.stored_packets.append(r)
        self.lastpacket=DataSpecMessage() #once sent create one new
        self.incrementCounter()

    def reset_counter_to(self, lastseen):
        self.counter=lastseen

    def incrementCounter(self):
        self.counter+=1;