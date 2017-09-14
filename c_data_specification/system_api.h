#ifndef _DATA_SPECIFICATION_SYSTEM_API_H
#define _DATA_SPECIFICATION_SYSTEM_API_H

#ifdef EMULATE
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef uint32_t* address_t;

#define spin1_exit(code) \
    return (code);
#define spin1_memcpy(destination, source, size) \
    memcpy((destination), (source), (size))
#define rt_error(error_code) \
    exit((error_code))
#define RTE_ABORT	-1
#define log_info(message, ...) \
    printf("[INFO] " message "\n", ##__VA_ARGS__)
#define log_warning(message, ...) \
    printf("[WARNING] " message "\n", ##__VA_ARGS__)
#define log_error(message, ...) \
    printf("[ERROR] " message "\n", ##__VA_ARGS__)
#define log_debug(message, ...) \
    printf("[DEBUG] " message "\n", ##__VA_ARGS__)
#define sark_xalloc(heap, size, tag, flag) \
    malloc((size))
#define sark_alloc(count, size) \
    malloc((count) * (size))
#define sark_xfree(heap, ptr, flag) \
    free((ptr))
#define sark_free(ptr) \
    free((ptr))

#else // !EMULATE
#include <spin1_api.h>
#include <debug.h>
#include <spinnaker.h>
#include <data_specification.h>
#endif // EMULATE

#endif // _DATA_SPECIFICATION_SYSTEM_API_H
