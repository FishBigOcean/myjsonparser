# -*- coding: utf-8 -*-
from jsonparser import Jsonparser, Parser_exception
import unittest, json, logging, os, filecmp

class Test_parser(unittest.TestCase):
    def setUp(self):
        self.parser = Jsonparser()
        self.json_ok = [
            ('{}', 1),
            ('{"":""}', 1),
            ('{"a":123}', 1),
            ('{"a":-123}', 1),
            ('{"a":1.23}', 1),
            ('{"a":1e1}', 1),
            ('{"a":true,"b":false}', 1),
            ('{"a":null}', 1),
            ('{"a":[]}', 1),
            ('{"a":{}}', 1),
            (' {"a:": 123}', 1),
            ('{ "a  " : 123}', 1),
            ('{ "a" : 123    	}', 1),
            ('{"true": "null"}', 1),
            ('{"":"\\t\\n"}', 1),
            ('{"\\"":"\\""}', 1),
            ('{"中\u4e2d\\u4e2d":"\\r"}', 1),
        ]
        self.json_ok2 = [
            ('{"a":' + '1' * 310 + '.0' + '}', 2),
            ('{"a":"abcde,:-+{}[]"}', 2),
            ('{"a": [1,2,"abc"]}', 2),
            ('{"a": {"a": {"a": 123}}}', 2),
            ('{"a": {"a": {"a": [1,2,[3]]}}}', 2),
            ('{"a": "\\u7f51\\u6613CC\\"\'"}', 3),
            ('{"d{": "}dd", "a":123}', 2),
            ('{"a":1e-1, "cc": -123.4}', 2),
            ('{ "{ab" : "}123", "\\\\a[": "]\\\\"}', 3),
        ]
        self.json_ex = [
            # exceptions
            ('{"a":[}', 2),
            ('{"a":"}', 2),
            ('{"a":True}', 1),
            ('{"a":Null}', 1),
            ('{"a":foobar}', 2),
            ("{'a':1}", 3),
            ('{1:1}', 2),
            ('{true:1}', 2),
            ('{"a":{}', 2),
            ('{"a":-}', 1),
            ('{"a":[,]}', 2),
            ('{"a":.1}', 1),
            ('{"a":+123}', 1),
            ('{"a":1..1}', 1),
            ('{"a":--1}', 1),
            ('{"a":"""}', 1),
            ('{"a":"""}', 1),
            ('{"a":"\\"}', 1),
        ]

    def test_loads_dumps(self):
        print('test loads and dumps')
        print('*' * 100)
        print('test json_ok')
        for num, case in enumerate(self.json_ok):
            try:
                self.parser.loads(case[0])
            except Exception as e:
                logging.warning('loads error: json_ok %d %s' % (num, case[0]))
                raise e
            d = json.loads(case[0])
            if d != self.parser.dump_dict():
                logging.warning('dump_dict error: json_ok %d %s' % (num, case[0]))
                raise Exception
            js = json.dumps(d)
            if js != self.parser.dumps():
                logging.warning('dumps error: json_ok %d %s %s %s' % (num, case[0], js, self.parser.dumps()))
                raise Exception
            try:
                self.parser.load_dict(d)
            except Exception as e:
                logging.warning('load_dict error: json_ok %d %s' % (num, case[0]))
                raise e
            if d != self.parser._data:
                logging.warning('load_dict error: json_ok %d %s' % (num, case[0]))
                raise Exception

        print('test json_ok2')
        for num, case in enumerate(self.json_ok2):
            try:
                self.parser.loads(case[0])
            except Exception as e:
                logging.warning('loads error: json_ok2 %d %s' % (num, case[0]))
                raise e
            if num == 17:
                print(d, self.parser.dump_dict())
            d = json.loads(case[0])
            if d != self.parser.dump_dict():
                logging.warning('dump_dict error: json_ok2 %d %s' % (num, case[0]))
                raise Exception

        print('test json_ex')
        for num, case in enumerate(self.json_ex):
            try:
                self.parser.loads(case[0])
            except Parser_exception as e:
                # print(e.info)
                continue
            logging.warning('loads error: json_ex %d %s' % (num, case[0]))
            raise Exception
        print('Pass all test cases')
        print('*' * 100)

    def test_load_file_dump_file(self):
        print('test load_file and dump_file')
        print('*' * 100)
        path = './test_case/json_test'
        out_path = './test_case/json_result'
        file_list = os.listdir(path)
        file_list.sort()
        for num, file in enumerate(file_list):
            file_dir = os.path.join(path, file)
            try:
                self.parser.load_file(file_dir)
            except Exception as e:
                logging.warning('load_file error: %d %s' % (num, file))
                raise e
            with open(file_dir, 'r') as f_read:
                temp = json.load(f_read)
            if temp != self.parser.dump_dict():
                logging.warning('dumps error: %d %s' % (num, file))
                raise Exception
            try:
                self.parser.dump_file(os.path.join(out_path, file))
            except Exception as e:
                logging.warning('dump_file error: %d %s' % (num, file))
                raise e
            self.assertTrue(filecmp.cmp(os.path.join(path, file), os.path.join(out_path, file)))
        print('*' * 100)

    def test_set_val_get_val_update(self):
        print('test set_val get_val update')
        print('*' * 100)
        js = '{"a":true,"b":false, "c": [1, 6.7, "d"]}'
        js2 = {'c': 0, 'd': None}
        self.parser.loads(js)
        d = json.loads(js)
        self.assertEqual(self.parser._data, d)
        self.assertEqual(self.parser['a'], True)
        self.assertEqual(self.parser['c'], d['c'])
        self.parser['c'] = 5
        self.assertEqual(self.parser['c'], 5)
        self.assertFalse(self.parser._data is self.parser.dump_dict())
        self.parser.updata(js2)
        self.assertEqual(self.parser['c'], 0)
        print('*' * 100)

if __name__ == '__main__':
    unittest.main()
