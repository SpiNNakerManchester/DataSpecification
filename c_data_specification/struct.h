#ifndef _STRUCT_H
#define _STRUCT_H

#include <stdint.h>

#define MAX_STRUCT_ELEMS 256

enum Type {
    Uint8  = 0x00,
    Uint16 = 0x01,
    Uint32 = 0x02,
    Uint64 = 0x03,
    Int8   = 0x04,
    Int16  = 0x05,
    Int32  = 0x06,
    Int64  = 0x07,
    U88    = 0x08,
    U1616  = 0x09,
    U3232  = 0x0A,
    S87    = 0x0B,
    S1615  = 0x0C,
    S3231  = 0x0D,
    U08    = 0x10,
    U016   = 0x11,
    U032   = 0x12,
    U064   = 0x13,
    S07    = 0x14,
    S015   = 0x15,
    S031   = 0x16,
    S063   = 0x17
};

typedef struct {
    uint64_t data;
    enum Type type;
} StructElement;

typedef struct {
    StructElement *elements;
    uint8_t size;
} Struct;

Struct *struct_new();
void struct_delete(Struct *str);
void struct_set_element_type(Struct *str, int elem_id, enum Type type);
void struct_set_element_value(Struct *str, int id, uint64_t value);
int data_type_get_size(enum Type type);
Struct *struct_create_copy(Struct *source);

#endif
