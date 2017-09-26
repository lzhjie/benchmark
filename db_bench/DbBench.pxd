# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
# cython: c_string_type=unicode, c_string_encoding=utf8
import cython


@cython.locals(size=long, last_index=long, failed_counter=long, index=long,
               step=long, next_level=long,)
cpdef benchmark(object theme, object data,
                object watch, object func,
                object conn, object func_hook)
