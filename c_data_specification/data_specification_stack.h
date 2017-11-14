#ifndef _DATA_SPECIFICATION_STACK
#define _DATA_SPECIFICATION_STACK

#define MAX_STACK_SIZE 64

//! \brief Function to insert a new element in the internal stack of DSE.
//! \param[in] new_item The value to be inserted.
void stack_push(void *new_item);

//! \brief Function to remove the first element of the internal stack of DSE.
//! \brief return The top of the stack.
void *stack_pop();

//! \brief Function to get the first element of the internal stack of DSE.
//! \brief return The top of the stack.
void *stack_top();

#endif
