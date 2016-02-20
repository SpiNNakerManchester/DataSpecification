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

class CommunicatorSender(object):

    def __init__(self, num_processes, dictionary, trns):

        self.trs=trns
        self.num_processes = num_processes
        self.involved_plmnt = dictionary

        self.semaphore=multiprocessing.Semaphore(num_processes)
        self.awake = True
        self.queue_of_writers = Queue()
        self.core_packet_sender=list()
        self.pkts_queue = Queue()
        self.sending_process=Process(target=self.packet_sender, args=(self.pkts_queue, self.trs))
        self.sending_process.start()
        self.receiver=Process(target=self.process_work, args=(self.pkts_queue, self.involved_plmnt,self.queue_of_writers, self.semaphore,  0, 30, 0))
        self.receiver.start()
        self.creators_queue=Queue()


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
        self.receiver.join()

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
        return self.queue_of_writers

    @staticmethod
    def manager_process(q):
        process=q.get(timeout=30)
        process.start()

    @staticmethod
    def packet_sender(q, trns):
        time.sleep(1)
        counter = 0
        while True:
            pass
            curr_params=q.get()
            if curr_params=="pause":
                #time.sleep(0.005)
                continue
            if curr_params=="pause_long":
                #time.sleep(0.1)
                continue
            if(curr_params == "stop"):
                logger.info('stop received')
                while True:
                    try:
                        curr_params=q.get(timeout=1)
                        if curr_params=="pause":
                            #time.sleep(0.002)
                            continue
                        if curr_params=="pause_long":
                            #time.sleep(0.1)
                            continue
                        hdr = curr_params[0]
                        pkt = curr_params[1]
                        trns.send_sdp_message(SDPMessage(hdr, pkt))
                        time.sleep(0.002)
                    except:
                        return
            else:
                hdr = curr_params[0]
                pkt = curr_params[1]
                trns.send_sdp_message(SDPMessage(hdr, pkt))
                time.sleep(0.003)

    @staticmethod
    def process_work(packets_queue, involveds, queue_from_spec, semaphore, iptag,future_id, report_flag):
        ENCODED_DELIMITERS = bytearray(struct.pack("<I", ((0x00 << 28) | (0XFF << 20)))) + struct.pack("<i", -1)
        laspacket_dict=dict()
        region_counter_flag_dict=dict()
        headers=dict()
        ended_status = dict()
        assert isinstance(involveds, dict)

        for key, value in involveds.iteritems():
            headers[key]=SDPHeader(flags=SDPFlag.REPLY_NOT_EXPECTED, destination_chip_x=key[0], destination_chip_y=key[1],destination_cpu=key[2],  destination_port=1)
            laspacket_dict[key]=DataSpecMessage()
            assert isinstance(value, list)
            datatoadd=struct.pack("<H", iptag)+struct.pack("<H", future_id)+struct.pack("<H", report_flag)
            laspacket_dict[key].add_row_initial_values(datatoadd)
            r=HostSendSequencedData(region_id=1, sequence_no=0, eieio_data_message=laspacket_dict[key])
            involveds[key].append(r.bytestring)
            header=headers[key]
            #packet=involveds[key][0]
            #packets_queue.put([header, packet])
            laspacket_dict[key].clean()
            region_counter_flag_dict[key] = [0, 1, True] #first region value, second counter, last waststored
            ended_status[key] = False

        #with semaphore:
        while True:
            cmd=queue_from_spec.get()
            actual_target=cmd[0]
            supported_target = False
            for k in involveds:
                if k == actual_target:
                    supported_target = True
                else:
                    continue

            if supported_target is False:
                logger.info("Unsupported Target")
                continue

            #logger.info('actual target '+ str(actual_target))
            cmdW=cmd[1]
            region = region_counter_flag_dict[actual_target][0]
            counter = region_counter_flag_dict[actual_target][1]
            if actual_target == (0,0,3):
                pass
            was_last_stored = region_counter_flag_dict[actual_target][2]
            lastpacket = laspacket_dict[actual_target]

            if( len(cmdW) > 200 ): #split it and send each subpacket
                #flush out the last packet if was still not sent
                if( (region_counter_flag_dict[actual_target][2]==False) and (laspacket_dict[actual_target]._len!=0)):
                    r=HostSendSequencedData(region_id=region, sequence_no=(region_counter_flag_dict[actual_target][1] % 256), eieio_data_message=laspacket_dict[actual_target])
                    involveds[actual_target].append(r.bytestring)
                    laspacket_dict[actual_target].clean() #once sent create one new
                    #counter+=1
                    region_counter_flag_dict[actual_target][1] += 1

                complete_pkts_to_do=int(len(cmdW)/200) #calc how many complete packets you have to do
                last_packet_len=(len(cmdW)%200) #calc the size of the last packet
                m = 200

                for i in range(0, complete_pkts_to_do): #iterate the number of complete packets

                    #lastpacket.clean()
                    if(i is 0):
                        laspacket_dict[actual_target].addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True, is_first_frag=True)
                    else:
                        if(i==(complete_pkts_to_do-1) and (last_packet_len is 0)): #is a multiple last packet
                            laspacket_dict[actual_target].addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True, is_last_frag=True)
                        else: #normal packet
                            laspacket_dict[actual_target].addFormattedCommand(cmdW[(i*m):((i*m)+m)], is_fragmented=True)

                    r=HostSendSequencedData(region_id=region, sequence_no=(region_counter_flag_dict[actual_target][1] % 256), eieio_data_message=laspacket_dict[actual_target])
                    involveds[actual_target].append(r.bytestring)
                    laspacket_dict[actual_target].clean() #once sent create one new
                    #counter+=1
                    region_counter_flag_dict[actual_target][1] += 1
                    region_counter_flag_dict[actual_target][2] = True

                if last_packet_len is not 0: #last packet
                    #lastpacket = DataSpecMessage()
                    laspacket_dict[actual_target].addFormattedCommand(cmdW[-last_packet_len:], is_fragmented=True, is_last_frag=True)
                    r=HostSendSequencedData(region_id=region, sequence_no=(region_counter_flag_dict[actual_target][1] % 256), eieio_data_message=laspacket_dict[actual_target])
                    involveds[actual_target].append(r.bytestring)
                    laspacket_dict[actual_target].clean() #once sent create one new
                    #counter+=1
                    region_counter_flag_dict[actual_target][1] += 1
                    region_counter_flag_dict[actual_target][2] = True
            else:
                #if many commands can be added put them in the same packet,
                # if you reach the measure limit (addFormattedCommand returns -1)
                # send the packet and add the current command (rejected from the other) to the next
                # or if you have to write the last sequence (isthelast=True) write and send it
                if(laspacket_dict[actual_target].addFormattedCommand(cmdW)<0): #if add to current fails
                    #too big for this packet send the last one (if was not sent yet)
                    if(region_counter_flag_dict[actual_target][2]==False and laspacket_dict[actual_target]._len!=0):
                        r=HostSendSequencedData(region_id=region, sequence_no=(region_counter_flag_dict[actual_target][1] % 256), eieio_data_message=laspacket_dict[actual_target])
                        involveds[actual_target].append(r.bytestring)
                        #counter+=1
                        region_counter_flag_dict[actual_target][1] += 1
                        region_counter_flag_dict[actual_target][2]=True

                    laspacket_dict[actual_target].clean()
                    laspacket_dict[actual_target].addFormattedCommand(cmdW)
                    if(cmdW == ENCODED_DELIMITERS): #force to send the last packet
                        #case final command that not fitted in the packet
                        r=HostSendSequencedData(region_id=3, sequence_no=(region_counter_flag_dict[actual_target][1] % 256), eieio_data_message=laspacket_dict[actual_target])
                        involveds[actual_target].append(r.bytestring)
                        ended_status[actual_target]=True
                        for i in involveds[actual_target]:
                            packets_queue.put([headers[actual_target], i])
                        #counter+=1
                        region_counter_flag_dict[actual_target][1] += 1
                        region_counter_flag_dict[actual_target][2]=True


                        all_ended=True
                        for k in ended_status:
                            if ended_status[k] == False:
                                all_ended=False

                        if all_ended:
                            return

                    region_counter_flag_dict[actual_target][2]=False
                else:
                    #if is the last command write it and send the whole last packet
                    if(cmdW == ENCODED_DELIMITERS):
                        #case final command that fitted in the last packet
                        r=HostSendSequencedData(region_id=3, sequence_no=(region_counter_flag_dict[actual_target][1] % 256), eieio_data_message=lastpacket)
                        involveds[actual_target].append(r.bytestring)
                        region_counter_flag_dict[actual_target][1] += 1
                        ended_status[actual_target]=True

                        nc = 0
                        for i in involveds[actual_target]:
                            nc += 1
                            packets_queue.put([headers[actual_target], i])
                            if nc == 20:
                                packets_queue.put("pause")
                        packets_queue.put("pause_long")
                        all_ended=True
                        for k in ended_status:
                            if ended_status[k] == False:
                                all_ended=False

                        if all_ended:
                            return

                    else: #if it is not the last packet and the add did not fail set that was not sent yet
                        region_counter_flag_dict[actual_target][2] = False
                #logger.info("ended")