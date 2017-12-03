# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>

import redis
from db_bench import DbConnection, multi_process_bench, Options


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
        k, v = record[0]
        return self.__client.set(str(k), str(v), nx=True) == True

    def search(self, record):
        k, v = record[0]
        return self.__client.get(str(k)) == str(v)

    def delete(self, record):
        k, v = record[0]
        return self.__client.delete(str(k)) == True

    def tear_down(self):
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
