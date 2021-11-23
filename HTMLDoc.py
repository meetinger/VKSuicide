from pprint import pprint

from utils import extract_from_dictionary

import re


class HTMLDoc:
    raw_data = ""
    data = []
    stack = []

    first_open_tag_index = 0
    last_open_tag_index = 0

    DEPTH_LIMIT = 5

    length = 0

    def __init__(self, raw_data: str):
        self.raw_data = raw_data
        self.length = len(raw_data)

    def build_path_str(self):
        res = []
        for i in self.stack:
            res.append(i)
            res.append('child')
        return res

    def get_doc(self):
        return self.data

    def parse(self):
        i = 0
        while i <= self.length:
            open_tag_res = re.match(r'<[^/]+?>', self.raw_data[i:])
            if open_tag_res is not None:
                # if len(self.stack) < self.DEPTH_LIMIT:
                open_tag = open_tag_res.group()
                path = self.build_path_str()
                tmp = extract_from_dictionary(self.data, path)

                tmp.append({'tag': open_tag, 'pos': i + open_tag_res.span()[0], 'endpos': -1, 'child': []})
                self.stack.append(len(tmp) - 1)
                i = i + open_tag_res.span()[1]
                continue

            close_tag_res = re.match(r'</\w+?>', self.raw_data[i:])
            if close_tag_res is not None:
                path = self.build_path_str()[:-1]
                tmp = extract_from_dictionary(self.data, path)
                print(tmp)
                tmp['endpos'] = i + close_tag_res.span()[1]
                self.stack.pop()
                # if len(self.stack) > self.DEPTH_LIMIT:
                #     tmp['child'] = self.data[tmp['pos']:tmp['endpos']]
                i = i + close_tag_res.span()[1]

            i = i + 1


string = '''<div>
                <a href="google.com" class="link"></a>
            </div>'''
# string = '''<a href="google.com" class="link blue"></a>'''



# print(parser.get_html_data())
