# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
from db_bench.DbBench import Options, Option
from db_bench.benchmarkjson2csv import json2csv
import os


def echarts(dir, csv_file=None):
    file_name = json2csv(dir) if csv_file is None else csv_file
    try:
        import pandas as pd
        from db_bench.csv2echartsjs import csv2js

        print(pd.read_csv(file_name, encoding="utf-8"))
        if os.name.lower() == "nt":  # windows
            csv2js(file_name, "echarts")
            import webbrowser
            webbrowser.open("file:///%s" % os.path.abspath("echarts/benchmark.html"))
        else:
            csv2js(file_name, dir)
    except:
        with open(file_name, "rb") as fp:
            print(fp.read().decode("utf-8"))


if __name__ == "__main__":
    options = Options.options
    options.append(Option("csv_file", "f", None))
    options = Options(options)
    if options.parse_option() is False:
        exit(100)
    out_dir = options.get("out_dir", "result")
    echarts(out_dir, options.get("csv_file"))
