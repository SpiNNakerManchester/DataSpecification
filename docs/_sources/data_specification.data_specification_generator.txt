data_specification.data_specification_generator module
======================================================

.. automodule:: data_specification.data_specification_generator

.. currentmodule:: data_specification.data_specification_generator

.. rubric:: Classes

.. autosummary::
    ArithmeticOperation
    Condition
    DataSpecificationGenerator
    DataType
    LogicOperation
    RandomNumberGenerator

.. autoclass:: ArithmeticOperation
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        ADD
        MULTIPLY
        SUBTRACT

.. autoclass:: Condition
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        EQUAL
        GREATER_THAN
        GREATER_THAN_OR_EQUAL
        LESS_THAN
        LESS_THAN_OR_EQUAL
        NOT_EQUAL

.. autoclass:: DataSpecificationGenerator
    :show-inheritance:

    .. rubric:: Methods

    .. autosummary::
        align_write_pointer
        break_loop
        call_arithmetic_operation
        call_function
        call_logic_operation
        call_random_distribution
        comment
        copy_structure
        copy_structure_parameter
        declare_random_number_generator
        declare_uniform_random_distribution
        define_struture
        else_conditional
        end_conditional
        end_function
        end_loop
        end_specification
        execute_break
        execute_no_operation
        free_memory_region
        print_struct
        print_text
        print_value
        reserve_memory_region
        save_write_pointer
        set_register_value
        set_structure_value
        set_write_pointer
        start_conditional
        start_function
        start_loop
        switch_write_focus
        write_array
        write_structure
        write_value

    .. rubric:: Detailed Methods

    .. automethod:: align_write_pointer
    .. automethod:: break_loop
    .. automethod:: call_arithmetic_operation
    .. automethod:: call_function
    .. automethod:: call_logic_operation
    .. automethod:: call_random_distribution
    .. automethod:: comment
    .. automethod:: copy_structure
    .. automethod:: copy_structure_parameter
    .. automethod:: declare_random_number_generator
    .. automethod:: declare_uniform_random_distribution
    .. automethod:: define_struture
    .. automethod:: else_conditional
    .. automethod:: end_conditional
    .. automethod:: end_function
    .. automethod:: end_loop
    .. automethod:: end_specification
    .. automethod:: execute_break
    .. automethod:: execute_no_operation
    .. automethod:: free_memory_region
    .. automethod:: print_struct
    .. automethod:: print_text
    .. automethod:: print_value
    .. automethod:: reserve_memory_region
    .. automethod:: save_write_pointer
    .. automethod:: set_register_value
    .. automethod:: set_structure_value
    .. automethod:: set_write_pointer
    .. automethod:: start_conditional
    .. automethod:: start_function
    .. automethod:: start_loop
    .. automethod:: switch_write_focus
    .. automethod:: write_array
    .. automethod:: write_structure
    .. automethod:: write_value

.. autoclass:: DataType
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        INT16
        INT32
        INT64
        INT8
        S015
        S031
        S063
        S07
        S1615
        S3231
        S87
        U016
        U032
        U064
        U08
        U1616
        U3232
        U88
        UINT16
        UINT32
        UINT64
        UINT8

.. autoclass:: LogicOperation
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        AND
        LEFT_SHIFT
        NOT
        OR
        RIGHT_SHIFT
        XOR

.. autoclass:: RandomNumberGenerator
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        MERSENNE_TWISTER

