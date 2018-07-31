# The name of the application to be built (binary will be this with a `.aplx`
# extension)
APP = data_specification_executor

LIBRARIES = $(SPINN_DIRS)/lib/libspinn_frontend_common.a -lspinn_common $(SPINN_DIRS)/lib/libspin1_api.a -lm

# Directory to create APLX files in (must include trailing slash)
APP_OUTPUT_DIR = ../data_specification/data_spec_sender/

# Directory to place compilation artefacts (must include trailing slash)
BUILD_DIR = build/

# A space-separated list of object files to be built into the executable. These
# .o files will be created from corresponding .c files (e.g. example.c in this
# case).
OBJECTS = data_specification_executor.o data_specification_stack.o struct.o c_main.o

CFLAGS += -DPRODUCTION_CODE

# The spinnaker_tools standard makefile
include $(SPINN_DIRS)/make/spinnaker_tools.mk

$(shell mkdir build)
all: $(APP_OUTPUT_DIR)$(APP).aplx

clean:
	$(RM) $(OBJECTS) $(BUILD_DIR)$(APP).elf $(BUILD_DIR)$(APP).txt $(APP_OUTPUT_DIR)$(APP).aplx $(TEST_TARGET) $(BUILD_TEST_DIR)*


# The directory which contains the source files
SRC_DIR=./

# The source files to be tested
SRCS = data_specification_executor.c data_specification_stack.c struct.c c_main.c
OBJS = data_specification_executor.o data_specification_stack.o struct.o c_main.o

# The directory which contains the test files
TEST_DIR=./unittests/

HEADERS=${wildcard $(SRC_DIR)*.h}
BUILD_TEST_DIR=./test_dir/

OBJS := $(OBJS:%.o=$(BUILD_TEST_DIR)%.o)

TEST_TARGET=$(BUILD_DIR)test_dse.so
TEST_SRCS=unittests/test_data_specification_executor.c

TEST_OBJS=./test_dir/test_data_specification_executor.o

CUTTER_FLAGS=${shell pkg-config --cflags cutter}
CUTTER_LIBS =${shell pkg-config --libs   cutter}

check: $(TEST_TARGET)
	cutter $(BUILD_TEST_DIR)

$(TEST_TARGET): $(TEST_OBJS) $(OBJS)
	gcc -std=c99 -shared  $(CUTTER_LIBS) $(OBJS) $(TEST_OBJS) -o $(BUILD_TEST_DIR)$@

$(BUILD_TEST_DIR)%.o: %.c $(TEST_SRCS) $(HEADERS)
	gcc -std=c99 -O -fPIC -DEMULATE -c  $(CUTTER_FLAGS) $< -I$(SRC_DIR) -I$(SPINN_INC_DIR) -o $@

$(TEST_OBJS): $(TEST_SRCS) $(HEADERS)
	gcc -std=c99 -O -fPIC -DEMULATE -c  $(CUTTER_FLAGS) $< -I$(SRC_DIR) -o $@
