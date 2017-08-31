# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import os, sys
if sys.version.startswith("3"):
    from ..db_bench.DbBench import *
else:
    sys.path.insert(0, os.path.dirname(__file__)+"/..")
    from db_bench.DbBench import *
