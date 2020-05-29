# json解析器的python3实现
## 1.jsonparser.py
jsonparser.py中包含六个类，分别为Jsonparser()，Convert()，Tokenizer()，Parser()，Pointer()，Parser_exception()。

整体流程：
  
读取json格式的数据：输入的数据首先用类型转换器Convert进行类型转换，所有数据统一转换为string类型，之后通过词法分析器Tokenizer
对sting进行词法分析，将string分解成为一个个token，最后使用语法分析器Parser对token序列进行语法分析，生成最终的dict。

输出实例内容：把dict通过类型转换器Convert转换成需要的输出类型，之后输出。


### 1.1 Jsonparser()
实现了json解析器的基本功能，可以从string、file、dict读取json格式的数据，也可以把实例中的内容转换为string、file、dict， 
支持用[]进行赋值、读写操作，类似dict，还可以使用update方法用dict更新实例中的数据。

#### (1)init():
初始化方法。

#### (2)setitem():
赋值方法，操作类似字典。

#### (3)loads()：
读取JSON格式数据。

#### (4)dumps():
将实例中的内容通过类型转换器转换成json格式返回。

#### (5)load_file():
从文件中读取JSON格式数据。

#### (6)dump_file():
将实例中的内容以JSON格式存入文件，文件若存在则覆盖。

#### (7)load_dict():
从dict中读取数据，存入实例中，若遇到不是字符串的key则忽略。

#### (8)dump_dict():
返回一个字典，包含实例中的内容。

#### (9)update():
用字典d更新实例中的数据，类似于字典的update。


### 1.2 Convert()
实现了所需要的各种类型数据之间的转换。

#### (1)init():
初始化方法。

#### (2)example2json():
将实例内容转换为json格式string。

#### (3)dict2json():
将dict转换为json格式sting。

#### (4)example2dict():
将实例内容转换为dict。

#### (5)deepcopy_dict():
对dict进行深拷贝。

#### (6)deepcopy_list():
对list进行深拷贝。

#### (7)keep_key():
对不是string类型的key进行过滤。

#### (8)dict2string():
将dict转换为json格式string。

#### (9)list2string():
将list转换为json格式string。


### 1.3 Tokenizer()
词法分析器，对json格式的string进行词法分析，其中词类型主要分为：
- 'BEGIN_OBJECT'： '{' jsonobject开始的标志
- 'END_OBJECT'： '}' jsonobject结束的标志
- 'BEGIN_ARRAY'： '[' jsonarray开始的标志
- 'END_ARRAY'： ']' jsonarray结束的标志
- 'END_FILE'： 文件结束标志
- 'COLON'： ':' 冒号，用于分隔object中的name和value
- 'COMMA'： ',' 用于分隔object或value
- 'STRING'： 可以作为object的name或者作为一个value
- 'NUMBER'： 符合json格式标准的数字
- 'OTHER'： null， true， false

词法解析器把json格式的string分解成为一个个token([类型，内容])，分解过程中只判断对应的token内容符不符合json格式对应类型的词法，
符合词法就进行下一个token的判断，不符合就报错。

#### (1)init():
初始化方法。

#### (2)run():
对json格式的string进行词法分析并输出分解后的tokens。

#### (3)check_null():
检查内容是否符合null词法。

#### (4)check_false():
检查内容是否符合false词法。

#### (5)check_true():
检查内容是否符合true词法。

#### (6)check_string():
检查内容是否符合string词法，即是否含有非法控制符，是否含有转义字符，是否含有\uxxxx形式的unicode编码。

#### (7)check_number():
检查内容是否符合number词法，即小数、指数合法性判断等。

#### (8)check_fraction():
判断是否符合小数词法。

#### (9)check_exponent():
判断是否符合指数词法。

#### (10)check_digit():
判断是否是数字。

#### (11)no_check():
无需进行词法判断的词类型：'BEGIN_OBJECT', 'END_OBJECT', 'BEGIN_ARRAY', 'END_ARRAY', 'COLON', 'COMMA'。

#### (12)check_whitespace():
过滤json格式string中的whitespace。


### 1.4 Parser()
语法分析器，对tokens进行语法分析，分为jsonobject分析和jsonarray分析，判断输入的tokens是否符合json格式语法，判断过程为逐个读取token并判断其类型是否
与期望类型一致，如果一致则更新dict内容并修改期望类型，不一致就报错。

#### (1)init():
初始化方法。

#### (2)run():
对tokens进行语法分析。

#### (3)parse_object():
对jsonobject进行语法分析。

#### (4)parse_array():
对jsonarray进行语法分析。


### 1.5 Pointer()
指针，在数据上进行前后移动并读取对应位置的值。

#### (1)init():
初始化方法。

#### (2)has_next():
判断当前位置是否合法。

#### (3)next():
读取数据并移动指针。

#### (4)has_and_next():
判断位置是否合法同时向后移动指针。

#### (5)pre_val():
读取前一个位置的值。

#### (6)pre_index():
向前移动指针。

#### (7)remain():
查看剩余数据的数量。


### 1.6 Parser_exception()
自定义的解析器异常类，可以打印出指定的异常信息。



#### (1)init():


#### (2)init():


#### (3)init():


#### (4)init():


#### (5)init():


#### (6)init():


#### (7)init():


#### (8)init():
