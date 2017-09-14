# The directory which contains the source files
SRC_DIR=.
CC = gcc -std=c99

# The source files to be tested
SRCS := data_specification_executor.c data_specification_stack.c struct.c c_main.c

# The directory which contains the test files
TEST_DIR := $(SRC_DIR)/unittests

HEADERS := ${wildcard $(SRC_DIR)/*.h}
BUILD_TEST_DIR := $(SRC_DIR)/test_dir

OBJS := $(SRCS:%.c=$(BUILD_TEST_DIR)/%.o)

TEST_TARGET=$(BUILD_TEST_DIR)/test_dse.so
TEST_SRCS=$(TEST_DIR)/test_data_specification_executor.c

TEST_OBJS=$(BUILD_TEST_DIR)/test_data_specification_executor.o

CUTTER_FLAGS=${shell pkg-config --cflags cutter}
CUTTER_LIBS =${shell pkg-config --libs   cutter}

build-test: $(TEST_TARGET)
check: $(TEST_TARGET)
	cutter $(BUILD_TEST_DIR)

# Disable ignored-qualifiers warning; it's an issue in cutter, not our code
CFLAGS = -O -fPIC -DEMULATE $(CUTTER_FLAGS) -Wno-format

$(TEST_TARGET): $(TEST_OBJS) $(OBJS)
	$(CC) -shared $(CUTTER_LIBS) $(OBJS) $(TEST_OBJS) -o $@

$(BUILD_TEST_DIR)/%.o: %.c $(TEST_SRCS) $(HEADERS)
	test -d $(BUILD_TEST_DIR) || mkdir -p $(BUILD_TEST_DIR)
	$(CC) $(CFLAGS) -c $< -I$(SRC_DIR) -o $@

$(TEST_OBJS): $(TEST_SRCS) $(HEADERS)
	test -d $(BUILD_TEST_DIR) || mkdir -p $(BUILD_TEST_DIR)
	$(CC) $(CFLAGS) -c $< -I$(SRC_DIR) -o $@

.PHONY: build-test check
