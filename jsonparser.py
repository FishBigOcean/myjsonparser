# -*- coding: utf-8 -*-

status = ['BEGIN_OBJECT', 'END_OBJECT', 'BEGIN_ARRAY', 'END_ARRAY', 'END_FILE', 'COLON', 'COMMA', 'STRING', 'NUMBER', 'OTHER']
status2char = {'BEGIN_OBJECT': '{', 'END_OBJECT': '}', 'BEGIN_ARRAY':'[', 'END_ARRAY': ']', 'COLON': ':', 'COMMA': ','}
char2status = {'{': 'BEGIN_OBJECT', '}': 'END_OBJECT', '[': 'BEGIN_ARRAY', ']': 'END_ARRAY', ':': 'COLON', ',': 'COMMA'}

class Jsonparser():
    def __init__(self):
        self._data = {}

    def __setitem__(self, key, value):
        d = {key: value}
        convert = Convert()
        js = convert.dict2json(d)
        tokenizer = Tokenizer(js)
        parser = Parser(tokenizer.run())
        res = parser.run()
        self._data.update(res)

    def __getitem__(self, item):
        if item in self._data:
            return self._data[item]
        raise Parser_exception('object key %s is illegal' % item)

    def loads(self, s):
        tokenizer = Tokenizer(s)
        parser = Parser(tokenizer.run())
        self._data = parser.run()

    def dumps(self):
        convert = Convert()
        return convert.example2json(self._data)
# unicode utf-8编码问题
    def load_file(self, f):
        with open(f, 'r') as file:
            js = file.read().encode('utf-8').decode("unicode_escape")
        tokenizer = Tokenizer(js)
        parser = Parser(tokenizer.run())
        self._data = parser.run()

    def dump_file(self, f):
        convert = Convert()
        js = convert.example2json(self._data)
        with open(f, 'w') as file:
            file.write(repr(js))

    def load_dict(self, d):
        convert = Convert()
        js = convert.dict2json(d)
        tokenizer = Tokenizer(js)
        parser = Parser(tokenizer.run())
        self._data = parser.run()

    def dump_dict(self):
        convert = Convert()
        return convert.example2dict(self._data)

    def updata(self, d):
        convert = Convert()
        js = convert.dict2json(d)
        tokenizer = Tokenizer(js)
        parser = Parser(tokenizer.run())
        res = parser.run()
        self._data.update(res)

class Convert():
    def __init__(self):
        self.data = None
        self.res = None
        self.dict = None

    def example2json(self, data):
        self.data = data
        self.res = []
        self.dict2string(self.data)
        return ''.join(self.res)

    def dict2json(self, data):
        self.data = data
        self.dict = {}
        self.keep_key()
        return self.example2json(self.dict)

    def example2dict(self, data):
        return self.deepcopy_dict(data)

    def deepcopy_dict(self, d):
        temp = {}
        for key in d:
            val = d[key]
            if isinstance(val, dict):
                temp[key] = self.deepcopy_dict(val)
            elif isinstance(val, list):
                temp[key] = self.deepcopy_list(val)
            else:
                temp[key] = val
        return temp

    def deepcopy_list(self, l):
        temp = []
        for val in l:
            if isinstance(val, dict):
                temp.append(self.deepcopy_dict(val))
            elif isinstance(val, list):
                temp.append(self.deepcopy_list(val))
            else:
                temp.append(val)
        return temp

    def keep_key(self):
        for key in self.data:
            if isinstance(key, str):
                self.dict[key] = self.data[key]

    def dict2string(self, d):
        self.res.append('{')
        for key in d:
            if not isinstance(key, str):
                raise Parser_exception('the key of object must be string')
            val = d[key]
            self.res.append('"')
            self.res.append(key)
            self.res.append('"')
            self.res.append(':')
            if isinstance(val, str):
                self.res.append('"')
                self.res.append(val)
                self.res.append('"')
            elif isinstance(val, dict):
                self.dict2string(val)
            elif isinstance(val, list):
                self.list2string(val)
            elif isinstance(val, bool) or val is None:
                v2s = {None: 'null', True: 'true', False: 'false'}
                print(val, v2s[val])
                self.res.append(v2s[val])
            elif isinstance(val, (float, int)):
                self.res.append(str(val))
            self.res.append(',')
        if self.res[-1] == ',':
            self.res[-1] = '}'
        else:
            self.res.append('}')
        return

    def list2string(self, l):
        self.res.append('[')
        for val in l:
            if isinstance(val, str):
                self.res.append('"')
                self.res.append(val)
                self.res.append('"')
            elif isinstance(val, dict):
                self.dict2string(val)
            elif isinstance(val, list):
                self.list2string(val)
            elif isinstance(val, bool) or val is None:
                v2s = {None: 'null', True: 'true', False: 'false'}
                self.res.append(v2s[val])
            elif isinstance(val, (float, int)):
                self.res.append(str(val))
            self.res.append(',')
        if self.res[-1] == ',':
            self.res[-1] = ']'
        else:
            self.res.append(']')
        return

class Tokenizer():
    def __init__(self, s):
        self.tokens = []
        self.pointer = Pointer(s)
        self.char2func = {'n': self.check_null, 'f': self.check_false, 't': self.check_true, '"': self.check_string,
                          '-': self.check_number, '{': self.no_check, '}': self.no_check, '[': self.no_check,
                          ']': self.no_check, ':': self.no_check, ',': self.no_check}

    def run(self):
        self.check_whitespace()
        while self.pointer.has_next():
            temp = self.pointer.next()
            if temp in self.char2func:
                self.char2func[temp]()
            elif temp.isdigit():
                self.check_number()
            else:
                raise Parser_exception('illegal input')
            self.check_whitespace()
        self.tokens.append(['END_FILE', None])
        return self.tokens

    def check_null(self):
        check_str = 'ull'
        if self.pointer.remain() >= 3:
            for i in range(3):
                if self.pointer.next() != check_str[i]:
                    break
            else:
                self.tokens.append(['OTHER', None])
                return
        raise Parser_exception('illegal input: null')

    def check_false(self):
        check_str = 'alse'
        if self.pointer.remain() >= 4:
            for i in range(4):
                if self.pointer.next() != check_str[i]:
                    break
            else:
                self.tokens.append(['OTHER', False])
                return
        raise Parser_exception('illegal input: false')

    def check_true(self):
        check_str = 'rue'
        if self.pointer.remain() >= 3:
            for i in range(3):
                if self.pointer.next() != check_str[i]:
                    break
            else:
                self.tokens.append(['OTHER', True])
                return
        raise Parser_exception('illegal input: true')

    def check_string(self):
        string = []
        escapes = {'"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u'}
        while self.pointer.has_next():
            temp = self.pointer.next()
            if ord(temp) < 32: # 0 - 31 is control characters
                raise Parser_exception('illegal input: control characters id %d' % ord(temp))
            elif temp == '\\':
                temp = self.pointer.has_and_next('illegal input: no char after \\')
                if temp in escapes:
                    string.append('\\')
                    string.append(temp)
                    if temp == 'u':
                        if self.pointer.remain() >= 4:
                            for i in range(4):
                                temp = self.pointer.next()
                                if temp.isdigit() or 'a' <= temp <= 'f' or 'A' <= temp <= 'F': # \uxxxx x is utf-8 code, rang from 0 - 9 or a - f or A - F
                                    string.append(temp)
                                else:
                                    break
                            else:
                                continue
                        raise Parser_exception('illegal input: utf-8')
                else:
                    raise Parser_exception('illegal input: escapes')
            elif temp == '"':
                self.tokens.append(['STRING', ''.join(string)])
                return
            else:
                string.append(temp)
        raise Parser_exception('illegal input: string')

    def check_number(self):
        string = []
        temp = self.pointer.pre_val()
        if temp == '-':
            string.append(temp)
            temp = self.pointer.has_and_next('illegal input: no number after minus sign')
            if not temp.isdigit():
                raise Parser_exception('illegal input: no number after minus sign')
        if temp == '0':
            string.append(temp)
            self.check_fraction(string)
            self.check_exponent(string)
        else:
            string.append(temp)
            self.check_digit(string)
            self.check_fraction(string)
            self.check_exponent(string)
        self.tokens.append(['NUMBER', ''.join(string)])
        return

    def check_fraction(self, string):
        if self.pointer.has_next():
            temp = self.pointer.next()
            if temp == '.':
                string.append(temp)
                temp = self.pointer.has_and_next('illegal input: no number in fraction')
                if temp.isdigit():
                    string.append(temp)
                    self.check_digit(string)
                else:
                    raise Parser_exception('illegal input: no number in fraction')
            else:
                self.pointer.pre_index()
        return

    def check_exponent(self, string):
        if self.pointer.has_next():
            temp = self.pointer.next()
            if temp == 'E' or temp == 'e':
                string.append(temp)
                temp = self.pointer.has_and_next('illegal input: no number in exponent')
                if temp == '-' or temp == '+':
                    string.append(temp)
                    temp = self.pointer.has_and_next('illegal input: no number in exponent')
                if temp.isdigit():
                    string.append(temp)
                    self.check_digit(string)
                else:
                    raise Parser_exception('illegal input: no number in exponent')
            else:
                self.pointer.pre_index()
        return

    def check_digit(self, string):
        while self.pointer.has_next():
            temp = self.pointer.next()
            if temp.isdigit():
                string.append(temp)
            else:
                self.pointer.pre_index()
                break
        return

    def no_check(self):
        temp = self.pointer.pre_val()
        self.tokens.append([char2status[temp], temp])
        return

    def check_whitespace(self):
        legal_whitespace = {32, 10, 13, 9}  # space, line feed, carriage return, horizontal tab
        while self.pointer.has_next():
            temp = self.pointer.next()
            if ord(temp) not in legal_whitespace:
                self.pointer.pre_index()
                break

class Parser():
    def __init__(self, tokens):
        self.data = {}
        self.pointer = Pointer(tokens)

    def run(self):
        temp = self.pointer.has_and_next('there is no json object')
        if temp[0] != 'BEGIN_OBJECT':
            raise Parser_exception('The outermost layer is not a json object')
        self.data = self.parse_object()
        temp = self.pointer.has_and_next('there is no END_FILE status')
        if temp[0] != 'END_FILE':
            raise Parser_exception('parsing errors: END_FILE')
        return self.data

    def parse_object(self):
        data = {}
        name = None
        next_status = {'STRING', 'END_OBJECT'}
        while self.pointer.has_next():
            temp = self.pointer.next()
            cur_status = temp[0]
            cur_val = temp[1]
            if cur_status in next_status:
                if cur_status == 'OTHER':
                    data[name] = cur_val
                    next_status = {'COMMA', 'END_OBJECT'}
                elif cur_status == 'NUMBER':
                    set_val = set(cur_val)
                    if '.' in set_val or 'e' in set_val or 'E' in set_val:
                        cur_val = float(cur_val)
                    else:
                        cur_val = int(cur_val)
                    data[name] = cur_val
                    next_status = {'COMMA', 'END_OBJECT'}   # # COMMA 逗号   COLON 冒号
                elif cur_status == 'BEGIN_OBJECT':
                    data[name] = self.parse_object()
                    next_status = {'COMMA', 'END_OBJECT'}
                elif cur_status == 'BEGIN_ARRAY':
                    data[name] = self.parse_array()
                    next_status = {'COMMA', 'END_OBJECT'}
                elif cur_status == 'STRING':
                    if self.pointer.pre_val(2)[0] == 'COLON':
                        data[name] = cur_val
                        # data[name] = cur_val.encode('utf-8').decode("unicode_escape")
                        next_status = {'COMMA', 'END_OBJECT'}
                    # elif self.pointer.pre_val(2)[0] in {'BEGIN_OBJECT', 'COMMA'}:
                    else:
                        name = cur_val
                        # name = cur_val.encode('utf-8').decode("unicode_escape")
                        next_status = {'COLON'}
                elif cur_status == 'COLON':
                    next_status = {'STRING', 'NUMBER', 'BEGIN_OBJECT', 'BEGIN_ARRAY', 'OTHER'}
                elif cur_status == 'COMMA':
                    next_status = {'STRING'}
                elif cur_status == 'END_OBJECT':
                    return data
            else:
                raise Parser_exception('parsing errors: %s cant connected after %s in object' % (cur_status, self.pointer.pre_val(2)[0]))
        raise Parser_exception('parsing errors: object')

    def parse_array(self):
        data = []
        next_status = {'STRING', 'NUMBER', 'BEGIN_OBJECT', 'BEGIN_ARRAY', 'END_ARRAY', 'OTHER'}
        while self.pointer.has_next():
            temp = self.pointer.next()
            cur_status = temp[0]
            cur_val = temp[1]
            if cur_status in next_status:
                if cur_status in {'STRING', 'OTHER'}:
                    data.append(cur_val)
                    next_status = {'COMMA', 'END_ARRAY'}
                elif cur_status == 'NUMBER':
                    set_val = set(cur_val)
                    if '.' in set_val or 'e' in set_val or 'E' in set_val:
                        cur_val = float(cur_val)
                    else:
                        cur_val = int(cur_val)
                    data.append(cur_val)
                    next_status = {'COMMA', 'END_ARRAY'}
                elif cur_status == 'BEGIN_OBJECT':
                    data.append(self.parse_object())
                    next_status = {'COMMA', 'END_ARRAY'}
                elif cur_status == 'BEGIN_ARRAY':
                    data.append(self.parse_array())
                    next_status = {'COMMA', 'END_ARRAY'}
                elif cur_status == 'COMMA':
                    next_status = {'STRING', 'NUMBER', 'BEGIN_OBJECT', 'BEGIN_ARRAY', 'OTHER'}
                elif cur_status == 'END_ARRAY':
                    return data
            else:
                raise Parser_exception('parsing errors: %s cant connected after %s in array' % (cur_status, self.pointer.pre_val(2)[0]))
        raise Parser_exception('parsing errors: array')

class Pointer():
    def __init__(self, data):
        self.data = data
        self.index = 0
        self.length = len(self.data)

    def has_next(self):
        return self.index < self.length

    def next(self):
        self.index += 1
        return self.data[self.index - 1]

    def has_and_next(self, s):
        if self.has_next():
            return self.next()
        raise Parser_exception(s)

    def pre_val(self, num = 1):
        return self.data[max(0, self.index - num)]

    def pre_index(self):
        self.index = max(0, self.index - 1)

    def remain(self):
        return self.length - self.index

class Parser_exception(Exception):
    def __init__(self, info):
        super().__init__(self)
        self.info = info
        print(self.info)

# s = '{"xiaojun": 3000000.0, "xiaojun": "中国\u4e2d\\t\\u4e2d", "abc": [125, "sdfasdf"]}'
# tokenizer = Tokenizer(s)
# js = tokenizer.run()
# parser = Parser(js)
# d = parser.run()
# print(s)
# print(js)
# print(d)

# fr = './testjson.json'
# fw = './testjson2.json'
# a = Jsonparser()
# a.load_file(fr)
# print(a._data)
# a["1"] = {"2": 3}
# a.dump_file(fw)

js = '{"login": [{"username": "bb", "password": "\\u4e2d\\t"}], "register": [5.6]}'
a = Jsonparser()
a.loads(js)
print(a._data)
js2 = a.dumps()
a["register"] = 2
d = {1:8}
a.updata(d)
print(a._data)
d2 = a.dump_dict()
print(d2, d2 is a._data)