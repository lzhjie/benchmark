# -*- coding: utf-8 -*-
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import sys

if sys.version_info.major >= 3:
    from DbBench import DbConnection, multi_process_bench, Options, Option, \
        Data, DataRandom, DataFile, DataRecord
else:
    from DbBench import DbConnection, multi_process_bench, Options, Option, \
        Data, DataRandom, DataFile, DataRecord
