from multiprocessing import Process, Queue
from data_specification.communicate_classes import DataSpecMessage
import spinnman.transceiver as transceiver
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.sdp.sdp_message import SDPMessage
from spinnman.messages.eieio.command_messages.host_send_sequenced_data import HostSendSequencedData
import struct
import time
import logging
import multiprocessing
logger=logging.getLogger(__name__)

debug=False

if debug:
    import pickle

class CorePacketListCreatorAsyncSend_2():

    def __init__(self, x, y, p, iptag, future_id=30, report_flag=0):

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
        self.transceiver = transceiver
        self.private_queue=Queue()

    def get_queue(self):
        return self.private_queue

class CommunicatorsPool(object):

    def __init__(self, num_processes, trns):
        self.semaphore=multiprocessing.Semaphore(num_processes)
        self.pkts_queue = Queue()
        self.processes = list()
        self.awake = True
        self.num_processes = num_processes
        self.trs=trns
        self.core_packet_sender=list()
        self.sending_process=Process(target=self.packet_sender, args=(self.pkts_queue, self.awake, self.trs))
        self.sending_process.start()
        self.queue_of_processes = Queue()
        #self.man_process=Process(target=self.manager_process, args=(self.queue_of_processes,))
        #self.man_process.start()
        self.process_queue=Queue()


    def get_queue(self):
        return self.pkts_queue

    def stop_and_wait_the_end(self):
        self.awake=False
        self.pkts_queue.put("stop")
        for p in self.processes:
            p.join()


    def stop(self):
        #for i in range(0,self.num_processes):
        self.pkts_queue.put("stop")
        self.sending_process.join()
        for p in self.processes:
            p.join()

    def emergency_stop(self):
        try:
            self.sending_process.terminate()
        except:
            pass

        for p in self.processes:
            try:
                p.terminate()
            except:
                pass

    def add_communicate_packet(self, x,y,p, iptag, future_id=30, report_flag=0):
        cplc=CorePacketListCreatorAsyncSend_2(x, y, p, iptag,future_id, report_flag)
        self.core_packet_sender.append(cplc)
        newq=cplc.get_queue()
        p=Process(target=self.process_work, args=(self.awake, self.pkts_queue, x, y, p, iptag, future_id, report_flag, newq, self.semaphore))
        p.start()
        self.processes.append(p)
        return cplc.get_queue()

    @staticmethod
    def manager_process(q):
        process=q.get(timeout=30)
        process.start()

    @staticmethod
    def packet_sender(q, state, trns):
        counter = 0
        while True:
            curr_params=q.get()
            if(curr_params == "stop"):
                #logger.info('now simultaneous')
                while True:
                    try:
                        curr_params=q.get(timeout=3)
                        '''
                        counter += 1
                        if (counter%2) == 0: #75
                             time.sleep(0.0024) #0.0015
                             counter = 0
                        '''
                        hdr = curr_params[0]
                        pkt = curr_params[1]
                        trns.send_sdp_message(SDPMessage(hdr, pkt))
                        #time.sleep(0.0015) #0.00319
                        #time.sleep(0.001875)
                        #time.sleep(0.0009375)
                        #time.sleep(0.0014)
                        time.sleep(0.0008)
                        #time.sleep(0.00046875)#NO
                    except:
                        return
            else:
                '''
                counter += 1
                if (counter%2) == 0: #75
                     time.sleep(0.0024) #0.0015
                     counter = 0
                '''
                hdr = curr_params[0]
                pkt = curr_params[1]
                trns.send_sdp_message(SDPMessage(hdr, pkt))
                #time.sleep(0.0014)
                time.sleep(0.0008)
                #time.sleep(0.001875) #0.00319
                #time.sleep(0.0009375) #0.00319
                #time.sleep(0.0005) #0.00020

    @staticmethod
    def process_work(awake, packets_queue, x, y, p, iptag,future_id, report_flag, queue_from_spec, semaphore):
        with semaphore:
            ENCODED_DELIMITERS = bytearray(struct.pack("<I", ((0x00 << 28) | (0XFF << 20)))) + struct.pack("<i", -1)
            #while awake == True:
            useful_datas=list()

            ds_p=p
            ds_chip_x=x
            ds_chip_y=y
            ds_port=1
            header = SDPHeader(flags=SDPFlag.REPLY_NOT_EXPECTED,
                              destination_cpu=ds_p,
                              destination_chip_x=ds_chip_x,
                              destination_chip_y=ds_chip_y,
                              destination_port=ds_port)
            iptag=iptag
            lastpacket = DataSpecMessage()
            datatoadd=struct.pack("<H", iptag)+struct.pack("<H", future_id)+struct.pack("<H", report_flag)
            lastpacket.add_row_initial_values(datatoadd)
            r=HostSendSequencedData(region_id=1, sequence_no=0, eieio_data_message=lastpacket)
            packets_queue.put([header, r.bytestring])
            was_last_stored=True
            lastpacket.clean()
            region=0
            counter=1
            if debug:
                pkts_list=list()
            while True:
                cmdW=queue_from_spec.get()

                #'''
                if cmdW =="test":
                    print 'test succesful'
                    return
                #'''
                if( len(cmdW) > 200 ): #split it and send each subpacket
                    #flush out the last packet if was still not sent
                    if( (was_last_stored==False) and (lastpacket._len!=0)):
                        r=HostSendSequencedData(region_id=region, sequence_no=(counter % 256), eieio_data_message=lastpacket)
                        packets_queue.put([header, r.bytestring])
                        if debug:
                            pkts_list.append([header, r.bytestring])
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
                        packets_queue.put([header, r.bytestring])
                        if debug:
                            pkts_list.append([header, r.bytestring])
                        lastpacket.clean() #once sent create one new
                        counter+=1
                        was_last_stored = True
                    if last_packet_len is not 0: #last packet
                        #lastpacket = DataSpecMessage()
                        lastpacket.addFormattedCommand(cmdW[-last_packet_len:], is_fragmented=True, is_last_frag=True)
                        r=HostSendSequencedData(region_id=region, sequence_no=(counter % 256), eieio_data_message=lastpacket)
                        packets_queue.put([header, r.bytestring])
                        if debug:
                            pkts_list.append([header, r.bytestring])
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
                            packets_queue.put([header, r.bytestring])
                            if debug:
                                pkts_list.append([header, r.bytestring])
                            #lastpacket.clean() #once sent create one new
                            counter+=1
                            was_last_stored=True
                        #and create a new one
                        lastpacket.clean()
                        lastpacket.addFormattedCommand(cmdW)
                        if(cmdW == ENCODED_DELIMITERS): #force to send the last packet
                            #case final command that not fitted in the packet
                            r=HostSendSequencedData(region_id=3, sequence_no=(counter % 256), eieio_data_message=lastpacket)
                            packets_queue.put([header, r.bytestring])
                            if debug:
                                pkts_list.append([header, r.bytestring])
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
                            packets_queue.put([header, r.bytestring])
                            if debug:
                                pkts_list.append([header, r.bytestring])
                            #lastpacket.clean() #once sent create one new
                            counter+=1
                            was_last_stored=True
                            break
                        else: #if it is not the last packet and the add did not fail set that was not sent yet
                            was_last_stored=False

            if debug:
                filename= "./serialized_packets/"+str(ds_chip_y) +"_"+ str(ds_chip_y)+"_" + str(ds_p)
                output = open(filename, 'wb')
                pickle.dump(pkts_list, output)
                output.close()
