# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import os, shutil
from db_bench.DbBench import DbConnection, multi_process_bench, Options, \
    Data, DataRandom, DataFile, DataRecord
from echarts_data import echarts


class EmptyConnection(DbConnection):
    name = "empty"

    def __init__(self, options):
        super(EmptyConnection, self).__init__(options)

    def disconnect(self):
        pass

    def connect(self):
        pass

    @DbConnection.benchmark(u"增加")
    def insert(self, record):
        return self._warm_up(record)

    @DbConnection.benchmark(u"删除")
    def delete(self, record):
        return self._warm_up(record)


class PythonDict(DbConnection):
    def __init__(self, options):
        super(PythonDict, self).__init__(options)
        self.__dict = None

    def disconnect(self):
        self.__dict = None

    def connect(self):
        self.__dict = {}

    def set_up(self):
        pass

    def tear_down(self):
        pass

    @DbConnection.benchmark(u"增加")
    def insert(self, record):
        k, v = record[0]
        self.__dict[k] = v
        return True

    @DbConnection.benchmark(u"查找")
    def search(self, record):
        k, v = record[0]
        return self.__dict[k] == v

    @DbConnection.benchmark(u"删除")
    def delete(self, record):
        k, v = record[0]
        return self.__dict.pop(k, None) is not None


if __name__ == "__main__":
    option = Options()
    out_dir = os.path.basename(__file__).split(".")[0]
    option.set("out_dir", out_dir)
    option.set("record_num", 1000000)
    option.set("processor_num", 1)
    if option.parse_option() is False:
        exit(100)
    print(option)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir, ignore_errors=True)
    option.set("quiet", False)
    option.set("tag", "-q false DataRecord")
    multi_process_bench(option, EmptyConnection, DataRecord)
    option.set("quiet", True)
    option.set("tag", "-q true DataRecord")
    multi_process_bench(option, EmptyConnection, DataRecord)
    option.set("tag", "-q true Data")
    multi_process_bench(option, EmptyConnection, Data)
    option.set("tag", "-q true DataRecord")
    multi_process_bench(option, PythonDict, DataRecord)
    option.set("tag", "-q true DataRandom")
    multi_process_bench(option, EmptyConnection, DataRandom)
    option.set("tag", "-q true DataFile")
    option.set("file", __file__)
    multi_process_bench(option, EmptyConnection, DataFile)

    echarts(out_dir)
