# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>

import datetime
from pymongo import MongoClient, DESCENDING
from imports import *


def record2dict(record):
    k, v = record[0]
    return {'key': k, 'value': v}


class PyMongoIS(DbConnection):
    def __init__(self, options):
        super(PyMongoIS, self).__init__(options)
        self.__coll = self.table
        self.__client = None
        self.__table = None

    def __del__(self):
        if self.__client is not None:
            self.__client.drop_database(self.__coll)

    def disconnect(self):
        pass

    def connect(self):
        self.__client = MongoClient(self.host, self.port)
        db = self.__client[self.__coll]
        self.__table = db[self.__coll]
        self.__table.create_index([("key", DESCENDING)])

    def insert(self, record):
        return self.__table.insert(record2dict(record)) is not None

    def search(self, record):
        k, v = record[0]
        return self.__table.find_one({"key": k}) == v

    # def update(self, record):
    #     return self.__table.update({"key":record.key()},
    #                                {"$set":{"value":record.value()}})["updatedExisting"]

    # def delete(self, record):
    #     return self.__table.delete_one({"key":record.key()}).deleted_count == 1

    def _warm_up(self, record):
        pass


if __name__ == "__main__":
    options = list(Options.options)
    options.append(Option("file", "f", "test.txt"))
    option = Options(options)
    option.set("port", 27017)
    option.set("file", "test.txt")
    if option.parse_option() is False:
        exit(100)
    print(option)
    result = multi_process_bench(option, PyMongoIS, DataFile)
    # print result
