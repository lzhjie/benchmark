# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
# cython: c_string_type=unicode, c_string_encoding=utf8
import cython

cdef class Record(object):
    cdef object __record
    cdef void set_all(self, object all)

ctypedef void (*record_set_all)(Record, object)

@cython.locals(size=long, last_index=long, failed_counter=long, index=long,
               step=long, next_level=long,
               k=object, v=object, record=Record,
               __func_record_set_all=record_set_all)
cpdef benchmark(object theme, object data,
                object watch, object func,
                object conn, object func_hook)