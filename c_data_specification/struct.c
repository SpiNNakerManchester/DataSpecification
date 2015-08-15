#include "data_specification_executor.h"
#include "struct.h"

struct Struct *struct_new(int no_of_elements) {
    struct Struct *newStruct = sark_alloc(1, sizeof(struct Struct));
    newStruct->elements = sark_alloc(1, no_of_elements * sizeof(struct StructElement));
    newStruct->size = no_of_elements;
    return newStruct;
}

void struct_delete(struct Struct *str) {
    for (int index = 0; index < str->size; index++)
        sark_free(str->elements);
    sark_free(str);
}

void struct_set_element_type(struct Struct *str, int elem_id, enum Type type) {
    str->elements[elem_id].type = type;
}

void struct_set_element_value(struct Struct *str, int id, uint64_t value) {
    // Clear the most significant bits so that just the required bits are
    // kept.
    uint64_t mask = ~0;
    mask >>= (8 * sizeof(mask) - 8 * data_type_get_size(str->elements[id].type));
    str->elements[id].data = value & mask;
}

int data_type_get_size(enum Type type) {
    if (type == Uint8 || type == Int8 || type == U08 || type == S07) {
        return 1;
    } else if (type == Uint16 || type == Int16 || type == U88 || type == S87
            || type == U016   || type == S015) {
        return 2;
    } else if (type == Uint32 || type == Int32 || type == U1616 || type == S1615
            || type == U032   || type == S031) {
        return 4;
    } else if (type == Uint64 || type == Int64 || type == U3232 || type == S3231
            || type == U064   || type == S063) {
        return 8;
    } else {
        log_info("Unknown data type %x", type);
        rt_error(RTE_ABORT);
    }
}

struct Struct *struct_create_copy(struct Struct *source) {
    struct Struct *new_struct = struct_new(source->size);
    for (int element_id = 0; element_id < source->size; element_id++) {
            spin1_memcpy(new_struct->elements, source->elements,
                         sizeof(struct StructElement) * source->size);
    }
    return new_struct;
}

