import time
from pprint import pprint
from HTMLAnalyzer import HTMLAnalyzer
import numpy as np

# import sys
#
# sys.setrecursionlimit(15000)

class HTMLDocument:
    document = []

    def __init__(self, data):
        if isinstance(data, str):
            parser = HTMLAnalyzer()
            parser.feed(data)
            self.document = parser.get_html_data()
        else:
            self.document = data
        # print(self.document)

    def get_elements_by_attributes_rec(self, var, attrs: dict):
        res = []
        if isinstance(var, list):
            for i in var:
                res.extend(self.get_elements_by_attributes_rec(i, attrs))
        elif isinstance(var, dict):
            flag = True
            for attr_key, attr_value in attrs.items():
                if var['child']:
                    res.extend(self.get_elements_by_attributes_rec(var['child'], attrs))
                if not ((attr_key in var['attrs']) and (
                        var['attrs'][attr_key] == attr_value or attr_value in var['attrs'][attr_key])):
                    flag = False
                    break
            if flag:
                res.append(var)

        return res

    def get_elements_by_attributes(self, attrs: dict):
        return self.get_elements_by_attributes_rec(self.document, attrs)

    def check_attributes_rec(self, var, attrs: dict):
        flag = False
        if isinstance(var, list):
            for i in var:
                if self.check_attributes_rec(i, attrs):
                    flag = True
        elif isinstance(var, dict):
            for attr_key, attr_value in attrs.items():
                if var['child']:
                    flag = self.check_attributes_rec(var['child'], attrs)
                if (attr_key in var['attrs']) and (
                        var['attrs'][attr_key] == attr_value or attr_value in var['attrs'][attr_key]):
                    flag = True
                    break
        return flag

    def check_attributes(self, attrs):
        return self.check_attributes_rec(self.document, attrs)

    def get_document(self):
        return self.document

    def __str__(self):
        return str(self.document)


