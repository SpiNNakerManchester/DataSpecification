#include "data_specification_executor.h"
#include "data_specification_stack.h"

void *stack[MAX_STACK_SIZE];
int stack_size = 0;

void stack_push(void *new) {
    if (stack_size + 1 > MAX_STACK_SIZE) {
        log_error("DSE stack is full.");
        rt_error(RTE_ABORT);
    }
    stack[stack_size++] = new;
}

void *stack_pop() {
    if (stack_size == 0) {
        log_error("DSE stack is empty.");
        rt_error(RTE_ABORT);
    }
    return stack[--stack_size];
}

void *stack_top() {
    if (stack_size == 0) {
        log_error("DSE stack is empty.");
        rt_error(RTE_ABORT);
    }
    return stack[stack_size - 1];
}

