import codecs
from abc import ABC
from html.parser import HTMLParser
from pprint import pprint

from utils import extract_from_dictionary


class HTMLAnalyzer(HTMLParser, ABC):
    HTMLData = []
    stack = []

    def build_path_str(self):
        res = []
        for i in self.stack:
            res.append(i)
            res.append('child')
        return res

    def handle_starttag(self, tag, attrs):
        path = self.build_path_str()
        tmp = extract_from_dictionary(self.HTMLData, path)
        attr_dict = {i[0]: i[1].split() for i in attrs if i[1] is not None}
        tmp.append({'tag': tag, 'attrs': attr_dict, 'child': []})
        self.stack.append(len(tmp) - 1)

    def handle_endtag(self, tag):
        self.stack.pop()

    def handle_startendtag(self, tag, attrs):
        path = self.build_path_str()
        tmp = extract_from_dictionary(self.HTMLData, path)
        attr_dict = {i[0]: i[1].split() for i in attrs if i[1] is not None}
        tmp.append({'tag': tag, 'attrs': attr_dict, 'child': []})

    def handle_data(self, data):
        path = self.build_path_str()
        tmp = extract_from_dictionary(self.HTMLData, path)
        tmp.append(data)

    def get_html_data(self):
        return self.HTMLData

