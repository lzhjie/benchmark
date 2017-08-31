# Copyright (C) zhongjie luo <l.zhjie@qq.com>
# coding: utf-8
from pymongo import MongoClient, DESCENDING
from db_bench.DbBench import DbConnection, multi_process_bench, Options


def record2dict(record):
    return {'key': record.key(), 'value': record.value()}


class PyMongo(DbConnection):
    def __init__(self, options):
        super(PyMongo, self).__init__(options)
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
        return self.__table.find_one({"key":record.key()}) is not None

    def update(self, record):
        return self.__table.update({"key":record.key()},
                                   {"$set":{"value":record.value()}})["updatedExisting"]

    def delete(self, record):
        return self.__table.delete_one({"key":record.key()}).deleted_count == 1


    def clear(self):
        self.__client.drop_database(self.__coll)
        db = self.__client[self.__coll]
        self.__table = db[self.__coll]


def api_example():
    table_name = "test_pymongo"
    client = MongoClient("127.0.0.1")
    table = client[table_name][table_name]
    table.create_index([("a", DESCENDING)])
    print table.insert({"a": 1})
    print table.update({"a": 4}, {"$set": {"a": 2}})["updatedExisting"]
    print table.find_one({"a": 2})
    print table.delete_one({"a": 2}).deleted_count
    print table.find_one({"a": 2})
    client.drop_database(table_name)


if __name__ == "__main__":
    option = Options()
    option.set("port", 27017)
    if option.parse_option() is False:
        exit(100)
    print(option)
    result = multi_process_bench(option, PyMongo)
    # print result
