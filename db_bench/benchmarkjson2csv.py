# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import os, re, json, sys


def find_files(dir, pattarn, recursion=False):
    result = []
    patt = re.compile(pattarn)
    for root, subdirs, files in os.walk(dir):
        for name in files:
            if patt.match(name) is not None:
                full_name = os.path.join(root, name)
                result.append(full_name)
        if not recursion:
            break
    return result


def json2csv(dir="."):
    columns = ["NAME", "SUM", "FAIL"]
    benchmark_col = set()
    benchmarks = []
    files = find_files(dir, "^benchmark.*?.json$")
    files.sort(key=lambda x: os.stat(x).st_ctime)
    for file in files:
        with open(file, "r") as fp:
            bench = json.load(fp)
        stat = bench["stat"]
        fail = 0
        sum = 0
        benchmark = {}
        for k, v in stat.items():
            label = v["label"]
            benchmark_col.add(label)
            benchmark[label] = v["qps"]
            fail += v["fail"]
            sum = max(sum, v["sum"])
        benchmark["SUM"] = sum
        benchmark["FAIL"] = fail
        name = os.path.basename(file).split(".")[0]
        name = name.split("_", 1)[1].replace(",", " ")
        benchmark["NAME"] = name
        benchmarks.append(benchmark)

    # print rows
    csv_file_name = "%s/benchmark.csv" % (dir)
    with open(csv_file_name, "wb") as fp:
        columns.extend(benchmark_col)
        bytes_utf8 = bytearray(",".join(columns), "utf-8")
        if sys.version_info.major >= 3:
            bytes_utf8 = bytes(bytes_utf8)
        fp.write(bytes_utf8)
        fp.write(b"\r\n")
        for benchmark in benchmarks:
            bytes_utf8 = bytearray(",".join([str(benchmark.get(col, 0)) for col in columns]), "utf-8")
            if sys.version_info.major >= 3:
                bytes_utf8 = bytes(bytes_utf8)
            fp.write(bytes_utf8)
            fp.write(b"\r\n")
    return csv_file_name


if __name__ == "__main__":
    json2csv()
