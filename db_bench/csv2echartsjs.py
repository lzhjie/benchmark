# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import json, os
import pandas as pd

default_columns = [("QPS_S","查询"), ("QPS_I","增加"),
                   ("QPS_U","修改"), ("QPS_D","删除"),
                   ("FAIL", "失败")]
default_title = "数据库性能报告"


def csv2js(file_csv, our_dir=".", columns=default_columns, title=default_title):
    cont = pd.read_csv(file_csv)
    csv_obj = {"title": title,
               "category": [item.replace("_", "\n", 3) for item in cont["NAME"].values],
               "series": []}
    series = csv_obj["series"]
    for k, v in columns:
        if cont[k].sum() > 0:
            series.append({"type": k, "legend": v,
                           "data": [int(x) for x in cont[k].values]})
    file_name = "%s/benchmark.js" % (our_dir)
    with open(file_name, "w") as fp:
        fp.write("var benchmark_data = ")
        fp.write(json.dumps(csv_obj))
    return file_name


if __name__ == "__main__":
    csv2js("../result/benchmark.csv")
