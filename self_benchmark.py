# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import os, shutil
from db_bench.DbBench import DbConnection, multi_process_bench, Options, \
    Data, DataRandom, DataFile, DataRecord
from db_bench.benchmarkjson2csv import json2csv


class EmptyConnection(DbConnection):
    name = "empty"
    def __init__(self,options):
        super(EmptyConnection, self).__init__(options)

    def __del__(self):
        pass

    def disconnect(self):
        pass

    def connect(self):
        pass

    def insert(self, record):
        return True


class PythonDict(DbConnection):
    def __init__(self, options):
        super(PythonDict, self).__init__(options)
        self.__dict = None

    def __del__(self):
        pass

    def disconnect(self):
        self.__dict = None

    def connect(self):
        self.__dict = {}

    def insert(self, record):
        self.__dict[record.key()] = record.value()
        return True


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
    multi_process_bench(option, PythonDict, DataRecord)
    option.set("tag", "-q false DataRandom")
    multi_process_bench(option, EmptyConnection, DataRandom)

    option.set("quiet", True)
    option.set("tag", "-q true DataRecord")
    multi_process_bench(option, EmptyConnection, DataRecord)
    multi_process_bench(option, PythonDict, DataRecord)
    option.set("tag", "-q true DataRandom")
    multi_process_bench(option, EmptyConnection, DataRandom)
    option.set("tag", "-q true Data")
    multi_process_bench(option, EmptyConnection, Data)
    option.set("tag", "-q true DataFile")
    option.set("file", __file__)
    multi_process_bench(option, EmptyConnection, DataFile)

    file_name = json2csv(out_dir)
    with open(file_name) as fp:
        print(fp.read())
    try:
        from db_bench.csv2echartsjs import csv2js
        if os.name.lower() == "nt":  # windows
            csv2js(file_name, "echarts")
            import webbrowser
            webbrowser.open("file:///%s" % os.path.abspath("echarts/benchmark.html"))
        else:
            csv2js(file_name, out_dir)
    except:
        import sys
        print(sys.exc_info())
