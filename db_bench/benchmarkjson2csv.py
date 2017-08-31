# Copyright (C) zhongjie luo <l.zhjie@qq.com>
# coding: utf-8
import os, re, json


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
    column = ("NAME", "QPS_I", "QPS_S", "QPS_U", "QPS_D", "SUM", "FAIL")
    rows = []
    files = find_files(dir, "^benchmark.*?.json$")
    files.sort(key=lambda x: os.stat(x).st_ctime)
    empty = {'fail': 0, 'qps': 0.0, 'sum': 0, 'cost': 0.0}
    for file in files:
        with open(file, "r") as fp:
            bench = json.load(fp)
        stat = bench["stat"]
        stat_i = stat.get("insert", empty)
        stat_s = stat.get("search", empty)
        stat_u = stat.get("update", empty)
        stat_d = stat.get("delete", empty)
        fail = stat_i["fail"] + stat_s["fail"] + stat_u["fail"] + stat_d["fail"]
        sum = stat_i["sum"]
        name = os.path.basename(file).split(".")[0]
        name = name.split("_", 1)[1].replace(",", " ")
        rows.append((name, stat_i["qps"], stat_s["qps"], stat_u["qps"], stat_d["qps"], sum, fail))
    # rows = sorted(rows, key=lambda x: x[0], reverse=True)
    # print rows
    csv_file_name = "%s/benchmark.csv" % (dir)
    with open(csv_file_name, "w") as fp:
        fp.write(",".join(column))
        fp.write("\n")
        for row in rows:
            fp.write(",".join([str(x) for x in row]))
            fp.write("\n")
    return csv_file_name


if __name__ == "__main__":
    json2csv()
