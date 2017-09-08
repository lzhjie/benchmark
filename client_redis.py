# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>

import redis
from db_bench.DbBench import DbConnection, multi_process_bench, Options


class StrictRedis(DbConnection):
    def __init__(self, options):
        super(StrictRedis, self).__init__(options)
        self.__db = 0
        self.__client = None

    def connect(self):
        self.__client = redis.StrictRedis(self.host, self.port, self.__db)

    def disconnect(self):
        self.__client = None

    def insert(self, record):
        return self.__client.set(record.key(), record.value(), nx=True) == True

    def search(self, record):
        return self.__client.get(record.key()) == record.value()

    def delete(self, record):
        return self.__client.delete(record.key()) == True

    def clear(self):
        self.__client.flushdb()


def api_example():
    pass


if __name__ == "__main__":
    option = Options()
    option.set("port", 6379)
    if option.parse_option() is False:
        exit(100)
    print(option)
    result = multi_process_bench(option, StrictRedis)
    # print result
