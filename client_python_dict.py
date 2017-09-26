# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
from db_bench.DbBench import DbConnection, multi_process_bench, Options


class PythonDict(DbConnection):
    def __init__(self, options):
        """collection=enum("","z","h")"""
        super(PythonDict, self).__init__(options)
        self.__client = None

    def connect(self):
        self.__client = {}

    def disconnect(self):
        self.__client = None

    def insert(self, record):
        k, v = record[0]
        self.__client[k] = v
        return True

    def search(self, record):
        k, v = record[0]
        return self.__client.get(k, None) == v

    def update(self, record):
        return self.insert(record)

    def delete(self, record):
        k, v = record[0]
        return self.__client.pop(k, None) is not None


def api_example():
    # see ssdb_lib/example.py
    pass


if __name__ == "__main__":
    from db_bench.DbBench import DataRecord
    option = Options()
    option.set("quiet", True)
    if option.parse_option() is False:
        exit(100)
    option.set("processor_num", 1)
    if option.get("record_num") < 100000:
        option.set("record_num", 100000)
    print(option)
    result = multi_process_bench(option, PythonDict, DataRecord)
    #print(result)
