# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>

import datetime
from imports import *
from ssdb_lib.SSDB import SSDB


class SsdbIS(DbConnection):
    def __init__(self, options):
        """collection=enum("","z","h")"""
        super(SsdbIS, self).__init__(options)
        self.__coll = self.table
        self.__client = None

    def connect(self):
        self.__client = SSDB(self.host, self.port)

    def disconnect(self):
        self.__client.close()

    def insert(self, record):
        k, v = record[0]
        return self.__client.request(self.__coll + 'set', [str(k), str(v)]).ok()

    # def search(self, record):
    #    return self.__client.request(self.__coll + 'get', [str(record.key())]).ok()

    # def delete(self, record):
    #     return self.__client.request(self.__coll + 'del', [str(record.key())]).ok()

    def _warm_up(self, record):
        pass


if __name__ == "__main__":
    options = list(Options.options)
    options.append(Option("file", "f", "test.txt"))
    option = Options(options)
    option.set("port", 8888)
    option.set("table", "")
    if option.parse_option() is False:
        exit(100)
    print(option)
    result = multi_process_bench(option, SsdbIS, DataFile)
    # print result
