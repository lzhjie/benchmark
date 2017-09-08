# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
from db_bench.benchmarkjson2csv import json2csv
from db_bench.csv2echartsjs import csv2js
from db_bench.DbBench import Options
import os


if __name__ == "__main__":
    options = Options()
    if options.parse_option() is False:
        exit(100)
    out_dir = options.get("out_dir", "result")
    file_name = json2csv(out_dir)
    if os.name.lower() == "nt":  # windows
        csv2js(file_name, "echarts")
        import webbrowser
        webbrowser.open("file:///%s" % os.path.abspath("echarts/benchmark.html"))
    else:
        csv2js(file_name, out_dir)
