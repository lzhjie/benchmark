# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>

import os, re


def find_files(dir, pattarn, recursion=False):
    result = []
    patt = re.compile(pattarn)
    for root, subdirs, files in os.walk(dir):
        for name in files:
            if patt.match(name) is not None:
                full_name = os.path.join(root, name)
                result.append(full_name)
        if not recursion:
            break
    return result


def file_size(filename):
    size = os.path.getsize(filename)
    return "%.2fM" % (size / 1024 / 1024)


class FileInfo:
    def __init__(self, name, id):
        self.__name = name
        self.__id = id
        size = float(os.path.getsize(name))
        self.__str = "(%s) %s %.3fM" % (self.__id, self.__name, size / 1024 / 1024)

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id

    def __str__(self):
        return self.__str

