from enum import Enum


class Commands(Enum):
    """set of opcodes for the spec executor"""

    BREAK                   = (0x00, "Halts spec execution with an error")
    NOP                     = (0x01, "No operation. Can be used as a filler")
    RESERVE                 = (0x02, "Reserves a block of memory ready for filling")
    FREE                    = (0x03, "Releases previously reserved memory")
    DECLARE_RNG             = (0x05, "Declares a new random number generator")
    DECLARE_RANDOM_DIST     = (0x06, "Declares a new random distribution")
    GET_RANDOM_NUMBER       = (0x07, "Returns a random number drawn from the given distribution")
    START_STRUCT            = (0x10, "Begins declaration of new structure")
    STRUCT_ELEM             = (0x11, "Declare single element in a structure")
    END_STRUCT              = (0x12, "Ends declaration of new structure")
    START_CONSTRUCTOR       = (0x20, "Begins definition of a function to write data structures to memory")
    END_CONSTRUCTOR         = (0x25, "Ends definition of the write function")
    CONSTRUCT               = (0x40, "Invokes a constructor to build a data structure")
    WRITE                   = (0x41, "Performs a simple write or block write operation")
    WRITE_ARRAY             = (0x42, "Performs a write from an array")
    WRITE_STRUCT            = (0x43, "Performs a write from a predefined structure")
    BLOCK_COPY              = (0x44, "Copies a block of data from one area to another")
    SWITCH_FOCUS            = (0x50, "Swap between different reserved memory regions to work on several at the same time")
    LOOP                    = (0x51, "Set-up a loop")
    BREAK_LOOP              = (0x52, "Early exit from a loop")
    END_LOOP                = (0x53, "End of a loop")
    IF                      = (0x55, "Perform a condition and execute the following instructions only if the condition is true")
    ELSE                    = (0x56, "Else clause for associated IF statement")
    END_IF                  = (0x57, "Close block of instructions begun with the IF instruction")
    MV                      = (0x60, "Place a value in a register, from an immediate or another register")
    GET_WR_PTR              = (0x63, "Copy current write address to a register")
    SET_WR_PTR              = (0x64, "Move the write pointer to a new location, either relative to the start of this reserved memory area or relative to the current write pointer")
    ALIGN_WR_PTR            = (0x65, "Moves the write pointer so that it points to the next block with a given address granularity")
    ARITH_OP                = (0x67, "Perform arithmetic operation with operand 2 coming from a register")
    LOGIC_OP                = (0x68, "Perform logical operation with operand 2 coming from a register")
    REFORMAT                = (0x6A, "Reformats a value in an internal register")
    COPY_STRUCT             = (0x70, "Create an identical copy of a structure")
    COPY_PARAM              = (0x71, "Copy a parameter from one structure to another")
    WRITE_PARAM             = (0x72, "Modify a single parameter in a structure using an immediate value or register held-value")
    WRITE_PARAM_COMPONENT   = (0x73, "Modify a single parameter in a structure")
    PRINT_VAL               = (0x80, "Output the value of a register to the screen")
    PRINT_TXT               = (0X81, "Print a text string to the screen")
    PRINT_STRUCT            = (0X82, "Print the current state of one structure to the screen")
    END_SPEC                = (0XFF, "Cleanly ends the parsing of the data specs")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
