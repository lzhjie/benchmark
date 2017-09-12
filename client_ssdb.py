# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>

from ssdb_lib.SSDB import SSDB
from db_bench.DbBench import DbConnection, multi_process_bench, Options


class Ssdb(DbConnection):
    def __init__(self, options):
        """collection=enum("","z","h")"""
        super(Ssdb, self).__init__(options)
        self.__coll = self.table
        self.__client = None

    def connect(self):
        self.__client = SSDB(self.host, self.port)

    def disconnect(self):
        self.__client.close()

    def insert(self, record):
        return self.__client.request(self.__coll+'set', [str(record.key()), record.value()]).ok()

    def search(self, record):
        return self.__client.request(self.__coll+'get', [str(record.key())]).ok()

    def delete(self, record):
        return self.__client.request(self.__coll+'del', [str(record.key())]).ok()


def api_example():
    # see ssdb_lib/example.py
    pass


if __name__ == "__main__":
    option = Options()
    option.set("port", 8888)
    option.set("table", "")
    if option.parse_option() is False:
        exit(100)
    print(option)
    result = multi_process_bench(option, Ssdb)
    # print result