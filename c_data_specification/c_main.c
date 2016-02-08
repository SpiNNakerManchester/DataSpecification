/*! \file data_specification_executor.c
 *
 *  \brief The implementation of the on-chip Data Specification Executor (DSG).
 */

#include "commands.h"
#include "constants.h"
// data_specification_executor.h includes all the required headers if are
// needed
#include "data_specification_executor.h"

//! Array to keep track of allocated memory regions.
//! Initialised with 0 (NULL) by default.
MemoryRegion *memory_regions[MAX_MEM_REGIONS];

//! \brief Get the value of user2 register.
//!
//! \return The value of user2.
uint32_t get_user2_value() {
    return ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user2;
}

//! \brief Get the value of user1 register.
//!
//! \return The value of user1.
uint32_t get_user1_value() {
    return ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user1;
}

//! \brief Get the value of user0 register.
//!
//! \return The value of user0.
uint32_t get_user0_value() {
    return ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user0;
}

//! \brief Pointer to a memory region that contains the currently executing
//!        data spec.
address_t execRegion = NULL;

//! \brief The parameter structure for the DSE
dse_data *dse_exec_data_struct;

//! \brief The size of the execRegion memory block.
int currentBlock_size = 0;

//! \brief The app identifier of the current executable.
uint8_t current_app_id;

//! \brief The app identifier of the following executable for which the 
//!        data is being prepared.
uint8_t future_app_id;

//! \brief Pre-computed identifier for memory allocation for 
//         current executable
uint32_t current_sark_xalloc_flags;

//! \brief Pre-computed identifier for memory allocation for 
//         following application for which the data is being prepared
uint32_t future_sark_xalloc_flags;

//! \brief boolean to identify if the data structure for the memory map
//         report should be produced
uint8_t generate_report;

//! \brief memory are to store info related to the regions, to be used for
//         memory map report
MemoryRegion *report_header_start = NULL;

//! \brief Allocate memory for the header and the pointer table.
void pointer_table_header_alloc() {
    log_info("Allocating memory for pointer table");
    address_t header_start = sark_xalloc(sv->sdram_heap,
                                     HEADER_SIZE_BYTES + POINTER_TABLE_SIZE_BYTES,
                                     0x00,                       // tag
                                     future_sark_xalloc_flags);  // flag
    if (header_start == NULL) {
        log_error("Could not allocate memory for the header and pointer table");
        spin1_exit(-1);
    }

    ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user0 = (uint)header_start;
    
    header_start[0] = APPDATA_MAGIC_NUM;
    header_start[1] = DSE_VERSION;
    
    log_info("Header address 0x%08x", header_start);
    
    if (generate_report)
    {
      report_header_start = sark_xalloc(sv->sdram_heap,
               sizeof(MemoryRegion) * MAX_MEM_REGIONS,
               0x00,                       // tag
               future_sark_xalloc_flags);  // flag
      
      if (report_header_start == NULL) {
          log_error("Could not allocate memory to store reporting information");
          spin1_exit(-1);
      }
      ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user1 = (uint)report_header_start;
      log_info("Report address 0x%08x", report_header_start);
    }
}

//! \brief Write the pointer table in the memory region specified by user0.
//! Must be called after the DSE has finished its execution so that the memory
//! regions are allocated.
void write_pointer_table() {
  
    // Pointer to write the pointer table.
    address_t base_ptr = (address_t)(((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user0);
    address_t pt_writer = base_ptr + HEADER_SIZE;

    // Iterate over the memory regions and write their start address in the
    // memory location pointed at by the pt_writer.
    // If a memory region has not been defined, 0 is written.
    for (int i = 0; i < MAX_MEM_REGIONS; i++, pt_writer++) {
        if (memory_regions[i] != NULL) {
            *pt_writer = (uint32_t) memory_regions[i]->start_address;

            log_info("Region %d address 0x%08x size %d bytes, %s", i,
                     *pt_writer,
                     memory_regions[i]->size,
                     memory_regions[i]->unfilled ? "unfilled" : "filled");
        } else {
            *pt_writer = 0;
        }
    }
}

void write_memory_structs_for_report() {
    MemoryRegion region_zero;
    
    region_zero.start_address = NULL;
    region_zero.size = 0;
    region_zero.unfilled = 0;
    region_zero.write_pointer = NULL;
    
    for (int i = 0; i < MAX_MEM_REGIONS; i++) {
        if (memory_regions[i] != NULL) {
            spin1_memcpy(&report_header_start[i], memory_regions[i], sizeof(MemoryRegion));
        } else {
            spin1_memcpy(&report_header_start[i], &region_zero, sizeof(MemoryRegion));
        }
    }
}

//! \brief Free all the allocated structures in the memory_regions array, used
//!        to store information about the allocated memory regions.
void free_mem_region_info() {
    for (int index = 0; index < MAX_MEM_REGIONS; index++)
        if (memory_regions[index] != NULL)
            sark_free(memory_regions[index]);
}


//MACROS
#define RESERVED_SDRAM_MEMORY 1024 * 16 //8000 //(in bytes!!) 1KB  //15 OK per Brunell
#define MAX_PACKET_SIZE 3000 //3KB //! the maximum size of a packet
#define MAX_SEQUENCE_NO 0xFF; // The maximum sequence number

static uint32_t incorrect_packets;

static bool send_packet_reqs;

//-----FLAGS------
volatile bool last_buffer_operation; //last operation made
volatile bool isdequeuing=false; //is in act the dequeuing operation
volatile bool iamwaiting=true; //I wait

//-----BUFFER infos------
static uint32_t buffer_region_size;
static uint8_t *buffer_region;
static uint8_t *end_of_buffer_region;
static uint8_t *write_pointer;
static uint8_t *read_pointer;
address_t addr;

static uint8_t iptag;//iptag of the host

//! Info of the message actually saved into the DTCM
static uint16_t* msg_from_sdram; // pointer to the sdram
static uint8_t pkt_last_sequence_seen;//track last sequence seen
uint32_t dumped_packets=0; //counter of dumped packets


//! The different buffer operations
typedef enum buffered_operations{
    BUFFER_OPERATION_READ,
    BUFFER_OPERATION_WRITE
}buffered_operations;


uint32_t space_available;
uint32_t final_seq=-1;

sdp_msg_t sdp_to_send;

uint32_t calculate_free_space(){
    //read write pointer and read pointer
    uint8_t *wp=write_pointer;
    uint8_t *rp=read_pointer;
    uint32_t avlb_space=0;

    if(wp>rp){
        //log_debug("we are in the case WP >= RP");
        space_available=((uint32_t)end_of_buffer_region- (uint32_t)wp)
        +( (uint32_t)rp- (uint32_t)buffer_region);
    }else if(wp<rp){
        //log_debug("we are in the case WP < RP");
        space_available=(uint32_t) rp - (uint32_t) wp;
    }else if ((rp == wp) && (last_buffer_operation == BUFFER_OPERATION_READ)) {
        //log_debug("we are in the case WP == RP and BUFFER_OPERATION_READ");
        space_available =(uint32_t) end_of_buffer_region - (uint32_t) wp +( (uint32_t)rp- (uint32_t)buffer_region);
    }
    return avlb_space;
}

void send_sdp_pkt(){
    //((uint32_t*)(sdp_to_send.data))[0]=pkt_last_sequence_seen;
    //sdp_to_send.data[0]=2;
    sdp_to_send.arg2=pkt_last_sequence_seen;
    //log_debug( "content sent via sdp-> %d",((uint32_t*)(sdp_to_send.data))[0]);
    spin1_send_sdp_msg(&sdp_to_send, 2);
    return;
}

void timer_callback(uint unused0, uint unused1) {

        //se sto aspettando pacchetti e la dequeuing non è impegnata
        //oppure se non aspetto più pacchetti ma l'ultima sequenza vista non coincide con quella finale
        if((iamwaiting && !isdequeuing) /* || (!iamwaiting && ((pkt_last_sequence_seen)!=final_seq))*/ ){
                if(write_pointer>read_pointer){
                    //log_debug("we are in the case WP >= RP");
                    space_available=((uint32_t)end_of_buffer_region- (uint32_t)write_pointer)
                    +( (uint32_t)read_pointer- (uint32_t)buffer_region);
                }else if(write_pointer<read_pointer){
                    //log_debug("we are in the case WP < RP");
                    space_available=(uint32_t) read_pointer - (uint32_t) write_pointer;
                }else if ((read_pointer == write_pointer) && (last_buffer_operation == BUFFER_OPERATION_READ)) {
                    //log_debug("we are in the case WP == RP and BUFFER_OPERATION_READ");
                    space_available =(uint32_t) end_of_buffer_region - (uint32_t) write_pointer +( (uint32_t)read_pointer- (uint32_t)buffer_region);
                }

                uint32_t treshold=10;
                //log_info("available space %d", space_available);
                //I am here and the communication did not end
                //send_sdp_pkt();

        }
        //log_info("incorrect packets-> %d", incorrect_packets);
        //log_info("last seq seen: %d", pkt_last_sequence_seen);
        //log_info("dumpd pkts: %d", dumped_packets);
        //fetch_and_process_packet();

}


static inline uint8_t compute_ds_packet_size(uint8_t* eieio_msg_ptr) {
        /*
        | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 |  0 |
        |_________frag__flags_____________|________length_actual_frag__________|
        */
        uint8_t data_hdr_value = eieio_msg_ptr[0];
        //log_info("the command length is: %d", data_hdr_value);
        return data_hdr_value;

}


static inline bool is_eieio_packet_in_buffer(void) {

    // If there is no buffering being done, there are no packets
    if (buffer_region_size == 0) {
        return false;
    }
    // There are packets as long as the buffer is not empty; the buffer is
    // empty if the pointers are equal and the last op was read
    return !((write_pointer == read_pointer) &&
            (last_buffer_operation == BUFFER_OPERATION_READ));

}

/*
static bool workingfragm=false; //bydefault
static bool reconstructed=false; //bydefault
uint32_t totallen=0;
*/
//bool frag_wrk=false;
uint32_t* stored_command=NULL;
uint32_t el_type_size=NULL;
int residual_size=0;
//uint32_t lst_command_len=0;
uint32_t counter=4;
uint8_t* lastseenwp;
uint8_t residual_fr[8];


void fetch_and_process_packet() {

    if(isdequeuing==false){
        isdequeuing=true;
        //uint32_t last_len = 2;
        //log_debug("in fetch_and_process_packet");
        // If we are not buffering, there is nothing to do
        /*
        if (buffer_region_size == 0) {
            //log_error("buffr_size is 0");
            return;
        }*/

        lastseenwp=write_pointer;
        while ( is_eieio_packet_in_buffer()) {
                //read the read_pointer value at this time and store it in temp_rp
                uint8_t* tem_rp=read_pointer;
                uint8_t *src_ptr = (uint8_t *) read_pointer;
                uint8_t *dst_ptr= (uint8_t *) msg_from_sdram;
                uint32_t pkt_len = compute_ds_packet_size(tem_rp);
                uint32_t len=pkt_len+1; //add the two bites of the chunk header (NOT counted from the host!!)
                //log_debug("pkt_len= %d",pkt_len);

                //lst_command_len=pkt_len;
                //log_info("content length-> %d", pkt_len);
                //last_len = len;
                if (len > MAX_PACKET_SIZE ) {
                    log_error("pkt big for DTCM allc", len);
                    rt_error(RTE_SWERR);
                    continue;
                }

                uint32_t final_space = (end_of_buffer_region - (tem_rp) );
                //log_debug("packet with length %d, from address: %08x", len,  read_pointer);

                if (len > final_space) { //len or cmd_len?
                    // If the packet is split, get the bits
                    log_debug("splitted packet");
                    //log_debug("1 - reading packet to %08x from %08x length: %d", (uint32_t) dst_ptr, (uint32_t) (src_ptr+2), final_space);
                    spin1_memcpy(dst_ptr, src_ptr, final_space);//skip first two bits of flags

                    uint32_t remaining_len = len - final_space;
                    dst_ptr += final_space;
                    src_ptr = buffer_region;
                    //log_debug("2 - reading packet to %08x from %08x length: %d",(uint32_t) dst_ptr, (uint32_t) src_ptr, remaining_len);

                    spin1_memcpy(dst_ptr, src_ptr, remaining_len); //you have nothing to skip here (no header, it's the continuing of the same message)
                    tem_rp = buffer_region + remaining_len;
                } else {
                    // If the packet is whole, get the packet
                    //log_debug("full packet");
                    //log_debug("1 - reading packet to %08x from %08x length: %d",
                      //        (uint32_t) dst_ptr, (uint32_t) src_ptr, len);
                    spin1_memcpy(dst_ptr, src_ptr, len);
                    tem_rp += len;
                    if (tem_rp >= end_of_buffer_region) {
                        tem_rp = buffer_region;
                    }
                }

                //CRITICAL SECTION
                //update the read pointer and the status (atomically, avoid inconsistency)
                uint cpsr = spin1_int_disable (); //START critical section
                    last_buffer_operation = BUFFER_OPERATION_READ;
                    read_pointer=tem_rp;
                spin1_mode_restore(cpsr); //END critical section

                //log_debug("command unpacking");

                uint8_t* dtcm_mem=(uint8_t*)msg_from_sdram; //operates with bytes
                //log_debug("frst_cmmd_flag= %d   frst_cmmd_len= %d", dtcm_mem[1] ,dtcm_mem[2]);
                uint8_t* cmd= dtcm_mem+1;
                int act_pkt_len=(int)(dtcm_mem[0]);
                uint16_t tot=1;
                uint8_t i=0;
                uint8_t flag= cmd[0] & 0b11;
                if(flag!=0){ //if the command is fragment it will take the whole packet (also the last if it is incomplete)
                        //log_debug("fragm");
                        if(flag==2){
                            //stored_command = *((uint32_t*)(cmd+2)); //command
                            spin1_memcpy(stored_command, cmd+2, 4);
                            //log_debug("first frag");
                            el_type_size=(cmd[5] & 0b1111);
                        }
                        uint8_t cmd_len=cmd[1]; //length of fragment of command
                        uint8_t values_len;
                        if(flag==2){
                            values_len=cmd_len-8;
                        }else{
                            values_len=cmd_len+residual_size;
                        }
                        int new_residual_size=values_len%el_type_size;

                        uint32_t numel=values_len/el_type_size;
                        //log_debug("numl %d , resid %d", numel, residual_size);

                        /*
                        address_t addr;
                        if(flag==2){
                            addr=sark_xalloc(((sv_t*)SV_SV)->sdram_heap, (cmd_len-new_residual_size), 0, 0x01);
                        }else{
                            addr=sark_xalloc(((sv_t*)SV_SV)->sdram_heap, (cmd_len+8+residual_size-new_residual_size), 0, 0x01);
                        }
                        */

                        //address_t addr=sark_alloc((cmd_len+residual_size-new_residual_size), 1);
                        //address_t is uint32_t
                        uint32_t* actual_status=addr;
                        //copy the command

                        spin1_memcpy(actual_status, stored_command, 4);
                        //log_debug("copied cmd-> %d", addr[0]);

                        actual_status++; //upload starting point

                        //copy the new element number
                        spin1_memcpy(actual_status, &numel, 4);
                        //log_debug("copied value-> %d", addr[1]);
                        actual_status++; //upload starting point


                        //manage previous residual (cpy it in the memory)
                        if(residual_size!=0){
                            //log_debug("residual size-> %d", residual_size);
                            //add the previous residual
                            for(int j=0;j<residual_size;j++){
                                spin1_memcpy(((uint8_t*)actual_status)+j, residual_fr+j, 1);//for previous residual
                            }
                            actual_status=((uint8_t*)actual_status)+residual_size;
                        }

                        if(flag==2){
                            spin1_memcpy(actual_status, ((uint32_t*)(cmd+2))+2, (cmd_len-new_residual_size-8));
                            data_specification_executor(addr, (cmd_len-new_residual_size));
                        }else{
                            spin1_memcpy(actual_status, (cmd+2), (cmd_len-new_residual_size));
                            data_specification_executor(addr, (cmd_len+8+residual_size-new_residual_size));
                        }
                        //log_info("Executing dataSpec");
    					//data_specification_executor(addr, (cmd_len+8+residual_size-new_residual_size));

                        //sark_xfree(((sv_t*)SV_SV)->sdram_heap, addr, 0); //free
                        //sark_free(addr); //free
                        if(new_residual_size!=0){ //save last piece and his size for reuse it the next time you call the command
                            for(int j=0;j<residual_size;j++){
                                residual_fr[j]=*(cmd+2+cmd_len-residual_size);
                            }
                        }
                        if(flag==3){ //is the last fragment
                            //process the packet and set the flag to false
                            //log_debug("last frag");
                            //frag_wrk=false;
                            //stored_command=NULL;
                            el_type_size=NULL;
                            residual_size=0;
                        }
                    continue;
                }

                while(1){
                    uint8_t cmd_len=cmd[1]; //the length of actual command in bytes
                    tot+=(cmd_len+2);
                    //log_debug("elab cmd: %d len: %d ", i, cmd_len);
                    spin1_memcpy(addr, cmd+2, cmd_len);
                    //log_debug("0x%08x", (uint32_t)(*((uint32_t*)addr)));
                    data_specification_executor(addr, cmd_len);
                    if( tot >= act_pkt_len ){
                        //log_debug("0x%08x", (uint32_t)(*((uint32_t*)(addr+cmd_len-4))));
                        //log_debug("0x%08x", (uint32_t)(*((uint32_t*)(addr+cmd_len-4))));
                        //log_debug("stopping at num %d", i);
                        break;
                    }
                    cmd=dtcm_mem+tot;
                    //i++;
                }
                //check if the writing pointer changed position
                //if writing pointer is not moving for a while (counter)
                //and the iswaiting is now true
                //send the alert
                /*
                if(lastseenwp==write_pointer && iamwaiting){
                    if((--counter)  == 0 ){
                        //log_info("POINTER STOPPED FOR A WHILE");
                    }
                }
                */
        }
        isdequeuing=false;
    }

}


static inline bool add_payload_to_sdram(uint8_t* eieio_msg_ptr, uint32_t length) {

    uint8_t *msg_ptr = eieio_msg_ptr;
    msg_ptr[0]=length-1;
    uint8_t *wp=write_pointer;
    uint8_t *rp=read_pointer;
    bool lbo=last_buffer_operation;
    /*
    log_debug("read_pointer = 0x%.8x, write_pointer= = 0x%.8x,"
              "last_buffer_operation == read = %d, packet length = %d",
              rp,  wp,
              lbo == BUFFER_OPERATION_READ, length);
    */
    if ((read_pointer < write_pointer) ||
            (read_pointer == write_pointer &&
                last_buffer_operation == BUFFER_OPERATION_READ)) {
        uint32_t final_space =
            (uint32_t) end_of_buffer_region - (uint32_t) write_pointer;

        if (final_space >= length) {
            //log_debug("Packet fits in final space of %d", final_space);
            //log_debug("received-> |%d|%d|%d|%d|", ((uint8_t*)msg_ptr)[0], ((uint8_t*)msg_ptr)[1],((uint8_t*)msg_ptr)[2],((uint8_t*)msg_ptr)[3]);
            spin1_memcpy(write_pointer, msg_ptr, length);
            //log_debug("stored-> |%d|%d|%d|%d|", ((uint8_t*)write_pointer)[0], ((uint8_t*)write_pointer)[1],((uint8_t*)write_pointer)[2],((uint8_t*)write_pointer)[3]);
            write_pointer += length;
            last_buffer_operation = BUFFER_OPERATION_WRITE;
            if (write_pointer >= end_of_buffer_region) {
                write_pointer = buffer_region;
            }
            return true;
        } else {

            uint32_t total_space =
                final_space +
                ((uint32_t) read_pointer - (uint32_t) buffer_region);
            if (total_space < length) {
                log_debug("No space %d B", total_space);
                return false;
            }

            //log_debug("Copying first %d bytes to final space of %d", final_space);
            spin1_memcpy(write_pointer, msg_ptr, final_space);
            write_pointer = buffer_region;
            msg_ptr += final_space;

            uint32_t final_len = length - final_space;
            //log_debug("splitted-Copying remaining %d bytes", final_len);
            spin1_memcpy(write_pointer, msg_ptr, final_len);
            write_pointer += final_len;
            last_buffer_operation = BUFFER_OPERATION_WRITE;
            if (write_pointer == end_of_buffer_region) {
                write_pointer = buffer_region;
            }
            return true;
        }
    } else if (write_pointer < read_pointer) {
        uint32_t middle_space =
            (uint32_t) read_pointer - (uint32_t) write_pointer;

        if (middle_space < length) {
            log_info("No enough spc middle %d B %d", middle_space, pkt_last_sequence_seen);
            return false;
        } else {
            //log_debug("Packet fits in middle of %d", middle_space);
            spin1_memcpy(write_pointer, msg_ptr, length);
            write_pointer += length;
            last_buffer_operation = BUFFER_OPERATION_WRITE;
            if (write_pointer == end_of_buffer_region) {
                write_pointer = buffer_region;
            }
            return true;
        }
    }
    log_info("Buff alrd full");
    return false;
}



static inline void eieio_command_parse_sequenced_data(
        uint16_t* eieio_msg_ptr, uint16_t length) { //it sees the HostSendSequencedData

    uint16_t data_hdr_value = eieio_msg_ptr[0];
    uint8_t pkt_type = (data_hdr_value >> 14) && 0x03;
    if (pkt_type != 0x01) return;   //if is not a command packet drop it!
    uint16_t pkt_command = data_hdr_value & (~0xC000);
    if(pkt_command!=7) return;      //if is not a command_sequenced_data

    uint16_t sequence_value_region_id = eieio_msg_ptr[1];
    uint16_t region_id = sequence_value_region_id & 0xFF;
    uint16_t sequence_value = (sequence_value_region_id >> 8) & 0xFF;
    uint8_t next_expected_sequence_no =
        (pkt_last_sequence_seen + 1) & MAX_SEQUENCE_NO;
    uint16_t* eieio_content_pkt = &eieio_msg_ptr[2];


    //log_debug("Received packet: %d", sequence_value);
    //log_info("write ponter-> %d \n read_pointer -> %d",write_pointer,read_pointer);

    if (sequence_value == next_expected_sequence_no) {

        if(region_id==3){ //it means that you have to stop at the seq number of this packet.
            iamwaiting=false;
            final_seq=sequence_value-1;
            //log_info("stop seq_n %d", final_seq);
        }

        if(region_id==1 && sequence_value==0){ //iptag will be sent by the host in a 16bit integer chunk
            //set the iptagValue
            iptag=eieio_content_pkt[0];
            future_app_id = eieio_content_pkt[1];
            //generate data structure for memory map report
            generate_report = eieio_content_pkt[2];
            future_sark_xalloc_flags = (future_app_id << 8) | ALLOC_ID | ALLOC_LOCK;
            //allocate memory for the table pointer
            log_info("set IPTAG %d, fut_id %d, rep_fl %d", iptag, future_app_id, generate_report);
            pointer_table_header_alloc();
            sdp_to_send.tag=iptag;
            pkt_last_sequence_seen = sequence_value;
            return;
        }

        // parse_event_pkt returns false in case there is an error and the
        // packet is dropped (i.e. as it was never received)
        //log_debug("add_payload_to_sdram");
        bool ret_value = add_payload_to_sdram((((uint8_t*)eieio_msg_ptr)+3),
                                                   length - 3);
        //log_debug("add_payload_to_sdram return value: %d", ret_value);

        if (ret_value) {
            pkt_last_sequence_seen = sequence_value;
            /*
            log_debug("Updating last sequence seen to %d",
                pkt_last_sequence_seen);*/
        } else {
            //log_debug("unable to buffer packet");
            incorrect_packets++;
        }
    }else{
        dumped_packets+=1;
        //NotExpectedSequence
        log_info("NES n: %d , exp: %d", sequence_value, next_expected_sequence_no);
    }

}



void sdp_packet_callback(uint mailbox, uint port) {
    //log_debug("in sdp_packet_callback");
    use(port);
    sdp_msg_t *msg = (sdp_msg_t *) mailbox;
    uint16_t length = msg->length;
    uint16_t* eieio_msg_ptr = (uint16_t*) &(msg->cmd_rc);
    eieio_command_parse_sequenced_data(eieio_msg_ptr, length - 8); //parse command and enqueue in SDRAM (making a copy of the content)
    uint8_t ret=spin1_trigger_user_event(0, 0); //trigger the queue server (if another one is still working it will fail)
    //log_debug("USER event returned %d", ret);
    spin1_msg_free(msg); //free memory (DTCM allocated)
}


void initialize(){
    //log_debug("initializing");
    //alloc the space for process command
    addr=sark_xalloc(((sv_t*)SV_SV)->sdram_heap, 250, 0, current_sark_xalloc_flags);
    //alloc the memory for load into memory the fragmented command
    stored_command=sark_xalloc(((sv_t*)SV_SV)->sdram_heap, 4, 0, current_sark_xalloc_flags);
    //alloc the buffer
    buffer_region = (uint8_t *)sark_xalloc(((sv_t*)SV_SV)->sdram_heap, RESERVED_SDRAM_MEMORY, 0, current_sark_xalloc_flags);
    //alloc the memory for the command
    msg_from_sdram = (uint16_t*) spin1_malloc(MAX_PACKET_SIZE); //malloc argument is in bytes returns a pointer to the start.

    if(buffer_region==NULL){
        //log_error("no heap alloc");
    }

    pkt_last_sequence_seen=MAX_SEQUENCE_NO;
    buffer_region_size=RESERVED_SDRAM_MEMORY;
    read_pointer = buffer_region;
    write_pointer = buffer_region;
    end_of_buffer_region = buffer_region + RESERVED_SDRAM_MEMORY;

    //Set parameters for SDP sending
    sdp_to_send.length = 8 + 16; //send via sdp message+command arg1 contains the spec of the core, arg2 the serial num
    sdp_to_send.flags = 0x7;
    sdp_to_send.tag = 0;
    sdp_to_send.dest_port = 0xFF;
    sdp_to_send.srce_port = (1 << 5) | spin1_get_core_id(); //returns in the bottom 5 bit the chip_id
    sdp_to_send.dest_addr = 0;
    sdp_to_send.srce_addr = spin1_get_chip_id();    //returns in the bottom 16 bit the chip_id
    /* arg1 content:

        |__________4_BYTE_______________________|___________3_BYTE_____________________|___________1_BYTE____________________|_________1__BYTE________________|
        | 31 | 30 | 29 | 28 | 27 | 26 | 25 | 24 | 23 | 22 | 21 | 20| 19 | 18 | 17 | 16 | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 |  0 |
        |________________DOESNT_MATTER_________________________|_____________________________CHIP_ID_____________________________________|_______CORE_ID______|

    */
    //arg2 will contain the sequence number
    sdp_to_send.arg1=((spin1_get_chip_id())<<5) | ( 0x1F & spin1_get_core_id()) ;

}

static inline finalize(){
    log_info("finalizing");
    sark_xfree(((sv_t*)SV_SV)->sdram_heap, buffer_region, 0); //free the buffer
    sark_free(msg_from_sdram); //free the message
    sark_xfree(((sv_t*)SV_SV)->sdram_heap, addr, 0); //free
    sark_xfree(((sv_t*)SV_SV)->sdram_heap, stored_command, 0); //free
}


void c_main(void) {


    //compute a few constants, valid for the entire DSE
    current_app_id = sark_app_id();
    current_sark_xalloc_flags = (current_app_id << 8) | ALLOC_ID | ALLOC_LOCK;

    //executing data specification

    initialize();
    //lower the priority number better the priority obtained
    spin1_callback_on(SDP_PACKET_RX, sdp_packet_callback, 0);
    spin1_callback_on(USER_EVENT, fetch_and_process_packet, 1);
    spin1_set_timer_tick(5000000); //argument has to be expressed in microseconds
    //spin1_set_timer_tick(300000); //argument has to be expressed in microseconds
    spin1_callback_on(TIMER_TICK, timer_callback, 2);
    //set_core_state(READY_TO_RECEIVE);
    spin1_start(FALSE); //it causes the call of event driven framework scheduler and here "stops" the sequential
                        //calls in the c_main, the execution will continue when spin1_exit() will be called


    finalize();
    //writing the content of the table pointer
    write_pointer_table();

    //write data structure, if required, with the data
    //for the memory map report
    if (generate_report)
      write_memory_structs_for_report();

    //freeing used memory structures in DTCM
    //this may be discarded if needed: the app_stop on this executable
    //would get rid of the data in DTCM
    free_mem_region_info();
}
