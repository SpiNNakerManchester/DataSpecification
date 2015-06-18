#define DS_ADDRESS              0x60000000

// MAGIC Numbers:
#define DSG_MAGIC_NUM                  0x5B7CA17E  // Data spec magic number
#define APPDATA_MAGIC_NUM              0xAD130AD6  // Application datafile magic number
#define DSE_VERSION                    0x00010000  // Version of the file produced by the DSE

// DSG Arrays and tables sizes:
#define MAX_REGISTERS                  16
#define MAX_MEM_REGIONS                16
#define POINTER_TABLE_SIZE             4 * MAX_MEM_REGIONS
#define HEADER_START_ADDRESS           SDRAM_TOP
#define POINTER_TABLE_START_ADDRESS    SDRAM_TOP +  APP_PTR_TABLE_HEADER_BYTE_SIZE
#define APP_PTR_TABLE_HEADER_BYTE_SIZE 8
