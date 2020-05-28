# -*- coding: utf-8 -*-
status = ['BEGIN_OBJECT', 'END_OBJECT', 'BEGIN_ARRAY', 'END_ARRAY', 'END_FILE', 'COLON', 'COMMA', 'STRING', 'NUMBER', 'OTHER']
status2char = {'BEGIN_OBJECT': '{', 'END_OBJECT': '}', 'BEGIN_ARRAY':'[', 'END_ARRAY': ']', 'COLON': ':', 'COMMA': ','}
char2status = {'{': 'BEGIN_OBJECT', '}': 'END_OBJECT', '[':'BEGIN_ARRAY', ']': 'END_ARRAY', ':': 'COLON', ',': 'COMMA'}


# class Jsonparser():
#     def __init__(self):
#         self._data = {}
#
#     def __setitem__(self, key, value):
#
#
#     def __getitem__(self, item):
#
#
#     def loads(self, s):
#
#
#     def dumps(self, s):
#
#
#     def load_file(self, f):
#
#
#     def dump_file(self, f):
#
#
#     def load_dict(self, d):
#
#
#     def dump_dict(self, f):
#
#
#     def updata(self, d):

class Tokenizer():
    def __init__(self, s):
        self.tokens = []
        self.pointer = Pointer(s)
        self.char2func = {'n': self.check_null, 'f': self.check_false, 't': self.check_true, '"': self.check_string,
                          '-': self.check_number, '{': self.no_check, '}': self.no_check, '[': self.no_check,
                          ']': self.no_check, ':': self.no_check, ',': self.no_check}

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

class Pointer():
    def __init__(self, data):
        self._data = data
        self.index = 0
        self.length = len(self._data)

    def has_next(self):
        return self.index < self.length

    def next(self):
        self.index += 1
        return self._data[self.index - 1]

    def has_and_next(self, s):
        if self.has_next():
            return self.next()
        raise Parser_exception(s)

    def pre_val(self):
        return self._data[max(0, self.index - 1)]

    def pre_index(self):
        self.index = max(0, self.index - 1)

    def remain(self):
        return self.length - self.index

class Parser_exception(Exception):
    def __init__(self, info):
        super().__init__(self)
        self.info = info
        print(self.info)

s = r'3.45687e0003456""'
# for ch in s:
#     print(ch)
t = Tokenizer(s)
t.run()
print(t.tokens)