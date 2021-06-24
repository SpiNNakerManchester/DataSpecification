Search.setIndex({docnames:["data_specification","data_specification.enums","data_specification.spi","index","modules"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.viewcode":1,sphinx:56},filenames:["data_specification.rst","data_specification.enums.rst","data_specification.spi.rst","index.rst","modules.rst"],objects:{"":{data_specification:[0,0,0,"-"]},"data_specification.DataSpecificationExecutor":{dsef:[0,2,1,""],execute:[0,3,1,""],get_constructed_data_size:[0,3,1,""],get_header:[0,3,1,""],get_pointer_table:[0,3,1,""],get_region:[0,3,1,""],mem_regions:[0,4,1,""]},"data_specification.DataSpecificationExecutorFunctions":{execute_break:[0,3,1,""],execute_end_spec:[0,3,1,""],execute_mv:[0,3,1,""],execute_reserve:[0,3,1,""],execute_set_wr_ptr:[0,3,1,""],execute_switch_focus:[0,3,1,""],execute_write:[0,3,1,""],execute_write_array:[0,3,1,""],mem_regions:[0,4,1,""]},"data_specification.DataSpecificationGenerator":{align_write_pointer:[0,3,1,""],break_loop:[0,3,1,""],call_arithmetic_operation:[0,3,1,""],call_function:[0,3,1,""],call_random_distribution:[0,3,1,""],comment:[0,3,1,""],copy_structure:[0,3,1,""],copy_structure_parameter:[0,3,1,""],create_cmd:[0,3,1,""],current_region:[0,4,1,""],declare_random_number_generator:[0,3,1,""],declare_uniform_random_distribution:[0,3,1,""],define_break:[0,3,1,""],define_structure:[0,3,1,""],else_conditional:[0,3,1,""],end_conditional:[0,3,1,""],end_function:[0,3,1,""],end_loop:[0,3,1,""],end_specification:[0,3,1,""],free_memory_region:[0,3,1,""],get_structure_value:[0,3,1,""],logical_and:[0,3,1,""],logical_left_shift:[0,3,1,""],logical_not:[0,3,1,""],logical_or:[0,3,1,""],logical_right_shift:[0,3,1,""],logical_xor:[0,3,1,""],no_operation:[0,3,1,""],print_struct:[0,3,1,""],print_text:[0,3,1,""],print_value:[0,3,1,""],read_value:[0,3,1,""],region_sizes:[0,4,1,""],reserve_memory_region:[0,3,1,""],save_write_pointer:[0,3,1,""],set_register_value:[0,3,1,""],set_structure_value:[0,3,1,""],set_write_pointer:[0,3,1,""],start_conditional:[0,3,1,""],start_function:[0,3,1,""],start_loop:[0,3,1,""],switch_write_focus:[0,3,1,""],write_array:[0,3,1,""],write_cmd:[0,3,1,""],write_repeated_value:[0,3,1,""],write_structure:[0,3,1,""],write_value:[0,3,1,""],write_value_from_register:[0,3,1,""]},"data_specification.MemoryRegion":{allocated_size:[0,4,1,""],increment_write_pointer:[0,3,1,""],max_write_pointer:[0,4,1,""],region_data:[0,4,1,""],remaining_space:[0,4,1,""],unfilled:[0,4,1,""],write_pointer:[0,4,1,""]},"data_specification.MemoryRegionCollection":{count_used_regions:[0,3,1,""],is_empty:[0,3,1,""],is_unfilled:[0,3,1,""],needs_to_write_region:[0,3,1,""],regions:[0,4,1,""]},"data_specification.constants":{APPDATA_MAGIC_NUM:[0,5,1,""],APP_PTR_TABLE_BYTE_SIZE:[0,5,1,""],APP_PTR_TABLE_HEADER_BYTE_SIZE:[0,5,1,""],DSE_VERSION:[0,5,1,""],DSG_MAGIC_NUM:[0,5,1,""],MAX_CONSTRUCTORS:[0,5,1,""],MAX_MEM_REGIONS:[0,5,1,""],MAX_PACKSPEC_SLOTS:[0,5,1,""],MAX_PARAM_LISTS:[0,5,1,""],MAX_RANDOM_DISTS:[0,5,1,""],MAX_REGISTERS:[0,5,1,""],MAX_RNGS:[0,5,1,""],MAX_STRUCT_ELEMENTS:[0,5,1,""],MAX_STRUCT_SLOTS:[0,5,1,""]},"data_specification.enums":{ArithmeticOperation:[1,1,1,""],Commands:[1,1,1,""],Condition:[1,1,1,""],DataType:[1,1,1,""],LogicOperation:[1,1,1,""],RandomNumberGenerator:[1,1,1,""]},"data_specification.enums.ArithmeticOperation":{ADD:[1,2,1,""],MULTIPLY:[1,2,1,""],SUBTRACT:[1,2,1,""]},"data_specification.enums.Commands":{ALIGN_WR_PTR:[1,2,1,""],ARITH_OP:[1,2,1,""],BLOCK_COPY:[1,2,1,""],BREAK:[1,2,1,""],BREAK_LOOP:[1,2,1,""],CONSTRUCT:[1,2,1,""],COPY_PARAM:[1,2,1,""],COPY_STRUCT:[1,2,1,""],DECLARE_RANDOM_DIST:[1,2,1,""],DECLARE_RNG:[1,2,1,""],ELSE:[1,2,1,""],END_CONSTRUCTOR:[1,2,1,""],END_IF:[1,2,1,""],END_LOOP:[1,2,1,""],END_SPEC:[1,2,1,""],END_STRUCT:[1,2,1,""],FREE:[1,2,1,""],GET_RANDOM_NUMBER:[1,2,1,""],GET_WR_PTR:[1,2,1,""],IF:[1,2,1,""],LOGIC_OP:[1,2,1,""],LOOP:[1,2,1,""],MV:[1,2,1,""],NOP:[1,2,1,""],PRINT_STRUCT:[1,2,1,""],PRINT_TXT:[1,2,1,""],PRINT_VAL:[1,2,1,""],READ:[1,2,1,""],READ_PARAM:[1,2,1,""],REFORMAT:[1,2,1,""],RESERVE:[1,2,1,""],SET_WR_PTR:[1,2,1,""],START_CONSTRUCTOR:[1,2,1,""],START_STRUCT:[1,2,1,""],STRUCT_ELEM:[1,2,1,""],SWITCH_FOCUS:[1,2,1,""],WRITE:[1,2,1,""],WRITE_ARRAY:[1,2,1,""],WRITE_PARAM:[1,2,1,""],WRITE_PARAM_COMPONENT:[1,2,1,""],WRITE_STRUCT:[1,2,1,""]},"data_specification.enums.Condition":{EQUAL:[1,2,1,""],GREATER_THAN:[1,2,1,""],GREATER_THAN_OR_EQUAL:[1,2,1,""],LESS_THAN:[1,2,1,""],LESS_THAN_OR_EQUAL:[1,2,1,""],NOT_EQUAL:[1,2,1,""]},"data_specification.enums.DataType":{FLOAT_32:[1,2,1,""],FLOAT_64:[1,2,1,""],INT16:[1,2,1,""],INT32:[1,2,1,""],INT64:[1,2,1,""],INT8:[1,2,1,""],S015:[1,2,1,""],S031:[1,2,1,""],S063:[1,2,1,""],S07:[1,2,1,""],S1615:[1,2,1,""],S3231:[1,2,1,""],S87:[1,2,1,""],U016:[1,2,1,""],U032:[1,2,1,""],U064:[1,2,1,""],U08:[1,2,1,""],U1616:[1,2,1,""],U3232:[1,2,1,""],U88:[1,2,1,""],UINT16:[1,2,1,""],UINT32:[1,2,1,""],UINT64:[1,2,1,""],UINT8:[1,2,1,""],decode_array:[1,3,1,""],decode_numpy_array:[1,3,1,""],encode:[1,3,1,""],encode_as_int:[1,3,1,""],encode_as_numpy_int:[1,3,1,""],encode_as_numpy_int_array:[1,3,1,""],max:[1,4,1,""],min:[1,4,1,""],numpy_typename:[1,4,1,""],scale:[1,4,1,""],size:[1,4,1,""],struct_encoding:[1,4,1,""]},"data_specification.enums.LogicOperation":{AND:[1,2,1,""],LEFT_SHIFT:[1,2,1,""],NOT:[1,2,1,""],OR:[1,2,1,""],RIGHT_SHIFT:[1,2,1,""],XOR:[1,2,1,""]},"data_specification.enums.RandomNumberGenerator":{MERSENNE_TWISTER:[1,2,1,""]},"data_specification.exceptions":{DataSpecificationException:[0,6,1,""],DataSpecificationSyntaxError:[0,6,1,""],DataUndefinedWriterException:[0,6,1,""],DuplicateParameterException:[0,6,1,""],ExecuteBreakInstruction:[0,6,1,""],FunctionInUseException:[0,6,1,""],InvalidCommandException:[0,6,1,""],InvalidOperationException:[0,6,1,""],InvalidSizeException:[0,6,1,""],NestedFunctionException:[0,6,1,""],NoMoreException:[0,6,1,""],NoRegionSelectedException:[0,6,1,""],NotAllocatedException:[0,6,1,""],ParameterOutOfBoundsException:[0,6,1,""],RNGInUseException:[0,6,1,""],RandomNumberDistributionInUseException:[0,6,1,""],RegionExhaustedException:[0,6,1,""],RegionInUseException:[0,6,1,""],RegionNotAllocatedException:[0,6,1,""],RegionOutOfBoundsException:[0,6,1,""],RegionUnfilledException:[0,6,1,""],StructureInUseException:[0,6,1,""],TablePointerOutOfMemoryException:[0,6,1,""],TypeMismatchException:[0,6,1,""],UnimplementedDSECommandError:[0,6,1,""],UnimplementedDSGCommandError:[0,6,1,""],UnknownConditionException:[0,6,1,""],UnknownTypeException:[0,6,1,""],UnknownTypeLengthException:[0,6,1,""],WrongParameterNumberException:[0,6,1,""]},"data_specification.spi":{AbstractExecutorFunctions:[2,1,1,""]},"data_specification.spi.AbstractExecutorFunctions":{execute_align_wr_ptr:[2,3,1,""],execute_arith_op:[2,3,1,""],execute_block_copy:[2,3,1,""],execute_break:[2,3,1,""],execute_break_loop:[2,3,1,""],execute_construct:[2,3,1,""],execute_copy_param:[2,3,1,""],execute_copy_struct:[2,3,1,""],execute_declare_rng:[2,3,1,""],execute_else:[2,3,1,""],execute_end_constructor:[2,3,1,""],execute_end_if:[2,3,1,""],execute_end_loop:[2,3,1,""],execute_end_spec:[2,3,1,""],execute_end_struct:[2,3,1,""],execute_free:[2,3,1,""],execute_get_random_rumber:[2,3,1,""],execute_get_wr_ptr:[2,3,1,""],execute_if:[2,3,1,""],execute_logic_op:[2,3,1,""],execute_loop:[2,3,1,""],execute_mv:[2,3,1,""],execute_nop:[2,3,1,""],execute_print_struct:[2,3,1,""],execute_print_txt:[2,3,1,""],execute_print_val:[2,3,1,""],execute_random_dist:[2,3,1,""],execute_read:[2,3,1,""],execute_read_param:[2,3,1,""],execute_reformat:[2,3,1,""],execute_reserve:[2,3,1,""],execute_reset_wr_ptr:[2,3,1,""],execute_set_wr_ptr:[2,3,1,""],execute_start_constructor:[2,3,1,""],execute_start_struct:[2,3,1,""],execute_struct_elem:[2,3,1,""],execute_switch_focus:[2,3,1,""],execute_write:[2,3,1,""],execute_write_array:[2,3,1,""],execute_write_param:[2,3,1,""],execute_write_param_component:[2,3,1,""],execute_write_struct:[2,3,1,""]},data_specification:{DataSpecificationExecutor:[0,1,1,""],DataSpecificationExecutorFunctions:[0,1,1,""],DataSpecificationGenerator:[0,1,1,""],MemoryRegion:[0,1,1,""],MemoryRegionCollection:[0,1,1,""],constants:[0,0,0,"-"],enums:[1,0,0,"-"],exceptions:[0,0,0,"-"],spi:[2,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","attribute","Python attribute"],"3":["py","method","Python method"],"4":["py","property","Python property"],"5":["py","data","Python data"],"6":["py","exception","Python exception"]},objtypes:{"0":"py:module","1":"py:class","2":"py:attribute","3":"py:method","4":"py:property","5":"py:data","6":"py:exception"},terms:{"0":[0,1,3],"1":[0,1,3],"10":1,"100":1,"101":1,"103":1,"104":1,"106":1,"11":1,"112":1,"113":1,"114":1,"115":1,"116":1,"12":[0,1,3],"128":1,"129":1,"13":1,"130":1,"14":1,"15":[0,1,3],"1534894462":0,"16":[0,1],"17":1,"18":1,"19":1,"2":[0,1,3],"20":1,"21":1,"22":1,"23":1,"255":[0,1,3],"2903706326":0,"3":1,"31":[0,3],"32":[0,1,3],"32767":[0,3],"32768":[0,3],"37":1,"4":[0,1,3],"5":[0,1,3],"6":1,"63":[0,3],"64":1,"65":1,"65536":0,"66":1,"67":1,"68":1,"69":1,"7":1,"72":0,"8":[0,1,3],"80":1,"81":1,"82":1,"83":1,"85":1,"86":1,"87":1,"9":1,"96":1,"99":1,"9999847":[0,3],"boolean":[0,3],"break":[0,1,2,3],"byte":[0,1,3],"case":4,"class":[0,1,2,3],"default":[0,3],"enum":[0,3,4],"float":[0,1,3],"function":[2,4],"int":[0,1,2,3],"new":[0,3],"return":[0,1,2,3],"short":2,"switch":[0,2,3],"throw":[0,3],"true":[0,3],"try":0,"while":[0,3],A:[0,2,3],AND:[0,1,3],And:0,IF:[0,1,2],If:[0,2,3],In:[0,3],It:[0,3],NOT:1,No:[0,2,3],OR:[0,1,3],The:[0,1,2,3],There:[0,3],These:3,__getitem__:3,__init__:3,__iter__:3,__len__:3,__setitem__:3,absolut:[0,3],abstract_executor_funct:0,abstractexecutorfunct:[0,2],accept:[0,3],accord:1,actual:[0,1,3],ad:[0,3],add:[1,2],address:[0,3],address_is_regist:[0,3],advanc:[0,3],against:[0,3],align:[0,3],align_wr_ptr:[1,2],align_write_point:[0,3],all:[0,3],alloc:[0,2,3],allocated_s:[0,3],allow:[0,3],alreadi:[0,2,3],also:[0,1,3],although:[0,3],amount:[0,3],an:[0,1,2,3],ani:[0,3],anoth:[0,2,3],api:4,app_ptr_table_byte_s:0,app_ptr_table_header_byte_s:0,appdata_magic_num:0,appli:[0,1,3],applic:0,ar:[0,1,3],architectur:[0,3],argument:[0,3],argument_by_valu:[0,3],arith_op:[1,2],arithmet:[0,1,2,3],arithmeticoper:[0,1,3],arrai:[0,1,2,3],array_valu:[0,3],ascii:[0,3],assign:[0,2,3],assumpt:[0,3],attempt:0,avail:[0,3],base:[0,1,2,3],becaus:[0,3],been:[0,3],befor:[0,3],begin:2,being:[0,3],between:[0,3],beyond:[0,3],big:[0,3],binari:[0,1,3],bit:[0,1,3],block:[0,2,3],block_copi:[1,2],bool:[0,3],bound:0,branch:2,break_loop:[0,1,2,3],breakpoint:0,buffer:[0,3],build:0,bytearrai:[0,3],cach:[0,3],call:[0,2,3],call_arithmetic_oper:[0,3],call_funct:[0,3],call_random_distribut:[0,3],can:[0,3],cannot:0,caus:[0,3],chang:[0,3],charact:[0,3],check:[0,3],chip:0,close:[0,3],close_writ:[0,3],cmd:[0,2,3],cmd_string:[0,3],cmd_word_list:[0,3],code:3,collect:[0,3],combined_document:3,come:[0,3],command:[0,1,2,3],comment:[0,3],compar:[0,3],comparison:1,complet:[0,2,3],complic:1,compress:[0,3],condit:[0,1,2,3],condition_id:0,configur:[0,3],connect:[0,3],consid:[0,3],constant:[3,4],construct:[0,1,2,3],contain:[0,3],content:4,context:0,convers:1,convert:[0,1,3],copi:[0,2,3],copy_param:[1,2],copy_struct:[1,2],copy_structur:[0,3],copy_structure_paramet:[0,3],core:[0,3],correspond:1,count_used_region:[0,3],counter:[0,3],counter_regist:[0,3],counter_register_id:[0,3],cpu:[0,3],creat:[0,3],create_cmd:[0,3],creation:[0,3],current:[0,2,3],current_region:[0,3],data:[0,1,2],data_is_regist:[0,3],data_length:0,data_regist:[0,3],data_specif:3,data_typ:[0,3],dataspecif:3,dataspecificationexcept:[0,3],dataspecificationexecutor:[0,3],dataspecificationexecutorfunct:[0,3],dataspecificationgener:[0,3],dataspecificationsyntaxerror:[0,2,3],datatyp:[0,1,3],dataundefinedwriterexcept:[0,3],debug:[0,3],decim:1,declar:[0,2,3],declare_random_dist:[1,2],declare_random_number_gener:[0,3],declare_rng:[1,2],declare_uniform_random_distribut:[0,3],decod:1,decode_arrai:1,decode_numpy_arrai:1,defin:[0,2,3],define_break:[0,3],define_structur:[0,3],definit:[0,2,3],depend:3,describ:[0,3],descript:1,desir:[0,2,3],dest_id:[0,3],destin:[0,3],destination_id:[0,3],destination_id_is_regist:[0,3],destination_is_regist:[0,3],destination_parameter_index:[0,3],destination_structure_id:[0,3],detect:[0,3],determin:[0,3],differ:2,direct:1,disregard:[0,3],disribut:2,distribut:[0,2,3],distribution_id:[0,3],document:3,doe:[0,2,3],done:[0,3],dse:[0,2,3],dse_vers:0,dsef:[0,3],dsg:[0,3],dsg_magic_num:0,due:1,duplic:[0,3],duplicateparameterexcept:[0,3],dure:[0,3],e:[0,3],each:[0,2,3],earli:2,either:[0,2,3],element:[0,2,3],els:[0,1,2,3],else_condit:[0,3],empti:[0,3],encod:[0,1,3],encode_as_int:1,encode_as_numpy_int:1,encode_as_numpy_int_arrai:1,end:[0,2,3],end_condit:[0,3],end_constructor:[1,2],end_funct:[0,3],end_if:[1,2],end_is_regist:[0,3],end_loop:[0,1,2,3],end_spec:[0,1,2,3],end_specif:[0,3],end_struct:[1,2],enough:[0,3],enumer:[0,3],equal:1,error:[0,2,3],evalu:[0,3],exce:[0,3],except:[2,3,4],execut:[0,2,3],execute_align_wr_ptr:2,execute_arith_op:2,execute_block_copi:2,execute_break:[0,2,3],execute_break_loop:2,execute_construct:2,execute_copy_param:2,execute_copy_struct:2,execute_declare_rng:2,execute_els:2,execute_end_constructor:2,execute_end_if:2,execute_end_loop:2,execute_end_spec:[0,2,3],execute_end_struct:2,execute_fre:2,execute_get_random_rumb:2,execute_get_wr_ptr:2,execute_if:2,execute_logic_op:2,execute_loop:2,execute_mv:[0,2,3],execute_nop:2,execute_print_struct:2,execute_print_txt:2,execute_print_v:2,execute_random_dist:2,execute_read:2,execute_read_param:2,execute_reformat:2,execute_reserv:[0,2,3],execute_reset_wr_ptr:2,execute_set_wr_ptr:[0,2,3],execute_start_constructor:2,execute_start_struct:2,execute_struct_elem:2,execute_switch_focu:[0,2,3],execute_writ:[0,2,3],execute_write_arrai:[0,2,3],execute_write_param:2,execute_write_param_compon:2,execute_write_struct:2,executebreakinstruct:[0,3],executor:[0,1,2,3],exist:[0,1],exit:[0,3],expand:[0,3],expect:[0,3],extern:[0,3],extra:[0,3],extract:2,fail:[0,3],fals:[0,3],field:2,file:[0,2,3],filenam:0,fill:[0,3],fillabl:[0,3],finish:[0,2,3],first:[0,3],fit:[0,3],fix:1,float64:1,float_32:1,float_64:1,focu:[0,2,3],follow:[0,1,3],format:1,found:[0,3],fraction:[0,3],free:[0,1,2,3],free_memory_region:[0,3],from:[0,2,3],function_id:[0,3],functioninuseexcept:[0,3],futur:[0,3],g:[0,3],gener:[0,1,2,3],get:[0,2,3],get_constructed_data_s:[0,3],get_head:[0,3],get_pointer_t:[0,3],get_random_numb:[1,2],get_region:[0,3],get_structure_valu:[0,3],get_wr_ptr:[1,2],given:[0,1,2,3],greater_than:1,greater_than_or_equ:1,ha:[0,3],halt:[0,3],handl:[0,2,3],hardwar:1,have:[0,3],header:[0,3],held:[0,3],helper:[0,3],here:[0,3],hold:[0,3],holder:[0,3],how:[0,3],i:[0,3],id:[0,3],identifi:[0,1,2,3],ignor:[0,3],imag:[0,3],immedi:[0,2,3],implement:[0,2,3],imposs:[0,3],includ:[0,3],inconsist:0,incorrect:[0,3],increment:[0,3],increment_is_regist:[0,3],increment_write_point:[0,3],index:[0,3],indic:0,inhibit:1,initialis:[0,3],input:1,insert:[0,3],instruct:[0,3],int16:1,int32:1,int64:1,int8:1,integ:[0,1,3],interact:0,interfac:2,intern:1,interven:[0,3],invalid:[0,3],invalidcommandexcept:[0,3],invalidoperationexcept:[0,3],invalidsizeexcept:[0,3],ioerror:[0,3],is_empti:[0,3],is_unfil:[0,3],isn:2,item:[0,3],item_id:0,item_typ:0,iter:[0,1,3],its:[0,3],kei:3,kept:[0,3],known:[0,3],label:[0,3],lack:1,languag:[0,3],larg:[0,3],larger:[0,3],later:[0,3],left:[0,3],left_shift:1,length:[0,3],less_than:1,less_than_or_equ:1,librari:[0,1,3],list:[0,3],locat:2,log:[0,2,3],log_block_s:[0,3],log_block_size_is_regist:[0,3],logic:[0,1,2,3],logic_op:[1,2],logical_and:[0,3],logical_left_shift:[0,3],logical_not:[0,3],logical_or:[0,3],logical_right_shift:[0,3],logical_xor:[0,3],logicoper:1,loop:[0,1,2,3],lost:[0,3],machin:0,made:[0,3],magic:0,mai:1,main:4,mani:[0,3],map:[0,3],mark:[0,2,3],marker:[0,2,3],max:[0,1,3],max_constructor:0,max_mem_region:0,max_packspec_slot:0,max_param_list:0,max_random_dist:0,max_regist:0,max_rng:0,max_struct_el:0,max_struct_slot:0,max_valu:[0,3],max_write_point:[0,3],maximum:[0,1,3],mem_region:[0,3],memori:[0,2,3],memory_avail:0,memory_requir:0,memory_spac:[0,3],memoryregion:[0,3],memoryregioncollect:[0,3],mention:[0,3],mersenne_twist:1,messag:0,method:[0,3],min:1,min_valu:[0,3],minimum:[0,1,3],mismatch:0,modul:[3,4],more:[0,3],move:[0,2,3],multipl:[0,3],multipli:1,must:[0,3],mv:[0,1,2,3],n_byte:[0,3],n_region:[0,3],name:0,ndarrai:[0,1,3],need:[0,2,3],needs_to_write_region:[0,3],nestedfunctionexcept:0,never:2,next:[0,2,3],no_of_parameters_requir:0,no_oper:[0,3],nomoreexcept:[0,3],non:[0,3],none:[0,1,2,3],nop:[1,2],noregionselectedexcept:[0,3],not_equ:1,notabl:1,notallocatedexcept:[0,3],note:[0,3],noth:[0,3],number:[0,1,2,3],numpi:[0,1,3],numpy_typenam:1,object:[0,2,3],obtain:2,occur:0,offset:0,onc:[0,3],one:[0,1,2,3],onli:[0,3],opcod:1,oper:[0,1,2,3],operand:[0,3],operand_1:[0,3],operand_1_is_regist:[0,3],operand_2:[0,3],operand_2_is_regist:[0,3],operand_is_regist:[0,3],operation_typ:0,optimis:[0,3],option:[0,3],origin:[0,3],other:2,otherwis:[0,3],out:[0,3],output:[0,3],outsid:[0,3],over:[0,3],overflow:[0,3],overwrit:[0,3],pack:0,packag:[3,4],page:3,paramet:[0,1,2,3],parameter_index:[0,3],parameter_index_is_regist:[0,3],parameteroutofboundsexcept:[0,3],pars:0,part:[0,3],pass:[0,3],pattern:1,per:[0,3],perform:[0,2,3],persist:[0,3],place:[0,3],point:[0,1,3],pointer:[0,2,3],posit:[0,3],possibl:[0,1,2,3],power:[0,3],previous:[0,3],print:[0,2,3],print_struct:[0,1,2,3],print_text:[0,3],print_txt:[1,2],print_val:[1,2],print_valu:[0,3],produc:[0,3],program:[0,2,3],project:3,properti:[0,1,3],provid:2,provis:[0,3],ptr:[0,3],purpos:0,put:[0,3],python:[1,3],question:0,rais:[0,2,3],ran:[0,3],random:[0,1,2,3],randomnumberdistributioninuseexcept:0,randomnumbergener:[0,1,3],rang:[0,3],range_max:0,range_min:0,rather:[0,3],rawiobas:[0,3],re:[0,3],reach:[0,3],read:[0,1,2,3],read_param:[1,2],read_valu:[0,3],receiv:[0,3],recommend:1,reduc:[0,3],refer:[0,3],referenc:[0,3],reformat:[1,2],region:[0,2,3],region_data:[0,3],region_id:[0,3],region_s:[0,3],regionexhaustedexcept:[0,3],regioninuseexcept:[0,3],regionnotallocatedexcept:[0,3],regionoutofboundsexcept:[0,3],regionunfilledexcept:[0,3],regist:[0,2,3],register_id:[0,3],relat:[0,2,3],relative_to_curr:[0,3],remain:[0,3],remaining_spac:[0,3],remov:[0,3],repeat:[0,3],repeats_is_regist:[0,3],report:[0,3],report_writ:[0,3],repres:[0,3],represent:1,request:[0,3],requested_offset:0,requested_operation_id:0,requir:[1,4],reserv:[0,1,2,3],reserve_memory_region:[0,3],reset:2,result:[0,3],return_register_id:[0,3],right:[0,3],right_shift:1,rng:0,rng_id:[0,3],rng_type:[0,3],rnginuseexcept:[0,3],run:[0,3],s015:1,s031:1,s063:1,s07:1,s1615:1,s3231:1,s87:1,s:[0,1,3],save:[0,3],save_write_point:[0,3],scale:1,sdram:[0,3],search:3,second:[0,3],see:[0,3],seed:[0,3],select:[0,3],set:[0,1,2,3],set_register_valu:[0,3],set_structure_valu:[0,3],set_wr_ptr:[0,1,2,3],set_write_point:[0,3],shift:[0,3],should:[0,3],shouldn:0,show:0,shrink:[0,3],sign:[0,3],signal:[0,2,3],singl:2,size:[0,1,3],skip:[0,3],slot:[0,2,3],slow:[0,3],small:[0,3],so:[0,3],some:[0,1,2,3],someth:0,sourc:[0,1,2,3],source_id_is_regist:[0,3],source_parameter_index:[0,3],source_structure_id:[0,3],space:[0,2,3],space_avail:0,space_requir:0,spec:[0,1,2,3],spec_read:[0,3],spec_writ:[0,3],special:[0,2,3],specif:[0,2],specifi:[0,2,3],spi:[0,3,4],spinnak:[0,1,3],spinnmachin:3,spinnutil:3,start:[0,2,3],start_address:[0,3],start_condit:[0,3],start_constructor:[1,2],start_funct:[0,3],start_is_regist:[0,3],start_loop:[0,3],start_struct:[1,2],statement:[0,3],still:1,stop:[0,2,3],storag:[0,3],store:[0,3],str:[0,1,3],string:[0,1,2,3],struct:1,struct_elem:[1,2],struct_encod:1,structur:[0,2,3],structure_id:[0,3],structure_id_is_regist:[0,3],structureinuseexcept:[0,3],subclass:2,submodul:[3,4],subpackag:[3,4],subtract:1,support:[1,2],switch_focu:[0,1,2,3],switch_write_focu:[0,3],syntax:[0,2,3],t:[0,2],tabl:0,tablepointeroutofmemoryexcept:[0,3],test:[0,3],text:[0,1,3],textiobas:[0,3],than:[0,3],thei:[0,2,3],them:[0,3],themselv:[0,3],thi:[0,1,2,3],through:[0,3],time:[0,2,3],too:[0,3],transfer:[0,3],trigger:[0,2,3],tupl:[0,1,3],two:[0,3],type:[0,1,2,3],type_id:0,type_nam:0,type_s:0,typemismatchexcept:0,u016:1,u032:1,u064:1,u08:1,u1616:1,u3232:1,u88:1,uint16:1,uint32:[0,1,3],uint64:1,uint8:1,unalloc:0,underli:[0,3],unfil:[0,3],uniform:[0,3],unimpl:0,unimplementeddsecommanderror:[0,2,3],unimplementeddsgcommanderror:0,unknown:[0,3],unknownconditionexcept:[0,3],unknowntypeexcept:[0,3],unknowntypelengthexcept:[0,3],unsign:[0,3],until:[0,3],up:[0,3],updat:[0,3],us:[1,2,4],valid:[0,3],valu:[0,1,2,3],value_is_regist:[0,3],variabl:[0,3],version:[0,3],vertex:[0,3],via:1,virtual:0,wa:[0,3],wai:[0,3],we:[0,3],went:0,what:0,when:[0,1,3],where:[0,3],whether:[0,1,3],which:[0,2,3],whichev:[0,3],whilst:0,whose:[0,3],wish:2,within:[0,3],word:[0,2,3],work:[0,2,3],would:[0,3],write:[0,1,2,3],write_arrai:[0,1,2,3],write_cmd:[0,3],write_param:[1,2],write_param_compon:[1,2],write_point:[0,3],write_repeated_valu:[0,3],write_struct:[1,2],write_structur:[0,3],write_valu:[0,3],write_value_from_regist:[0,3],writer:[0,3],written:[0,3],wrong:[0,3],wrongparameternumberexcept:[0,3],xor:[0,1,3],yet:[0,3],you:[0,3],zero:[0,3]},titles:["data_specification package","data_specification.enums package","data_specification.spi package","Data Specification","data_specification"],titleterms:{"case":[0,3],"enum":1,"function":[0,3],api:[0,3],constant:0,content:[0,1,2,3],data:3,data_specif:[0,1,2,4],except:0,indic:3,main:[0,3],modul:[0,1,2],packag:[0,1,2],requir:[0,3],specif:3,spi:2,submodul:0,subpackag:0,tabl:3,us:[0,3]}})