# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import json, os
import pandas as pd

default_title = "数据库性能报告"


def csv2js(file_csv, our_dir=".", title=default_title):
    cont = pd.read_csv(file_csv, encoding='utf-8')
    columns = set(cont.columns)
    except_columns = set(("NAME", "SUM", "FAIL"))
    columns -= except_columns
    csv_obj = {"title": title,
               "category": [item.replace("_", "\n", 3) for item in cont["NAME"].values],
               "series": []}
    series = csv_obj["series"]
    for column in columns:
        if cont[column].sum() > 0:
            series.append({"type": column,
                           "legend": column,
                           "data": [int(x) for x in cont[column].values]})
    file_name = "%s/benchmark.js" % (our_dir)
    with open(file_name, "w") as fp:
        fp.write("var benchmark_data = ")
        fp.write(json.dumps(csv_obj))
    return file_name


if __name__ == "__main__":
    csv2js("../result/benchmark.csv")
