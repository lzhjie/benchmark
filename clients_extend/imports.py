import os, sys

# Copyright (C) zhongjie luo <l.zhjie@qq.com>
if sys.version_info.major >= 3:
    from ..db_bench import *
else:
    sys.path.insert(0, os.path.dirname(__file__) + "/..")
    from db_bench.DbBench import *
