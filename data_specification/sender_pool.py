from multiprocessing import Process, Queue
from spinnman.messages.sdp.sdp_message import SDPMessage
from data_specification.communicate_classes import CorePacketListCreator
import time

class SenderPool(object):


    def __init__(self, num_processes, trns):

        self.params_queue = Queue()
        self.processes = list()
        self.awake = True
        self.num_processes = num_processes
        self.trs=trns
        for i in range(0,num_processes):
            #p=Process(target=self.work, args=(self.params_queue, self.awake, self.trs) )
            p=Process(target=self.work_perpacket, args=(self.params_queue, self.awake, self.trs) )
            self.processes.append(p)
            p.start()
        '''
        for i in range(0,num_processes):
            self.processes[i-1].join()
        '''

    def get_queue(self):
        return self.params_queue

    def add_packet(self, packet):
        self.params_queue.put(packet)

    def add(self, other):
        ml=list()
        pkt_lst_creator=other
        pk_list=other.stored_packets
        for i in pk_list:
            ml.append(i.bytestring)
        self.params_queue.put([other.header, ml])

    def stop(self):
        for i in range(0,self.num_processes):
            self.params_queue.put("stop")
        #for i in range(0,self.num_processes):
        #   self.processes[i-1].join()
        for p in self.processes:
            p.join()

    @staticmethod
    def work(q, state, trns):
        #print state
        #if isinstance(q, Queue()):
        while True:
            if not q.empty():
                curr_params=q.get()
                if(curr_params == 'stop'):
                    break
                else:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info('sending to a core')
                        hdr = curr_params[0]
                        pk_list = curr_params[1]
                        for i in pk_list:
                            trns.send_sdp_message(SDPMessage(hdr, i))
                            time.sleep(0.025)

    @staticmethod
    def work_perpacket(q, state, trns):
        counter = 0
        #print state
        #if isinstance(q, Queue()):
        while True:
            curr_params=q.get()
            if(curr_params == "stop"):
                break
            else:
                counter += 1
                if (counter%40) == 0: #75
                    time.sleep(0.008) #0.0015
                    counter = 0
                hdr = curr_params[0]
                pkt = curr_params[1]
                trns.send_sdp_message(SDPMessage(hdr, pkt))
                #time.sleep(0.0010) #0.00319
                time.sleep(0.0016) #0.00319
    '''
    @staticmethod
    def work_perpacket(q, state, trns):
        counter = 0
        #print state
        #if isinstance(q, Queue()):
        while True:
            if not q.empty():
                curr_params=q.get()
                if(curr_params == 'stop'):
                    break
                else:
                    counter += 1
                    if (counter%45) == 0: #75
                        time.sleep(10) #0.0015
                        counter = 0
                    hdr = curr_params[0]
                    pkt = curr_params[1]
                    trns.send_sdp_message(SDPMessage(hdr, pkt))
                    #time.sleep(0.0010) #0.00319
                    time.sleep(0.050) #0.00319
    '''