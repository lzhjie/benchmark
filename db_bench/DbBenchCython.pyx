# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import cython

cdef class RecordForCython:
    cdef object _key, _value
    cdef object _id
    cdef object _is_tail
    def __cinit__(self):
        pass

    cdef set_all(self, long key, long value, long id, bint is_tail):
        self._key = str(key)
        self._value = str(value)
        self._id = id
        self._is_tail = is_tail

    def key(self):
        return self._key

    def value(self):
        return self._value

    def id(self):
        return self._id

    def is_tail(self):
        return self._is_tail


@cython.locals(index = long)
cpdef benchmark_cython(theme, data, watch, func, func_hook, context):
    data.reset()
    record = RecordForCython()
    cdef long failed_counter = 0
    cdef long size = len(data)
    cdef long last_index = size - 1
    cdef long key = data.range_l
    cdef long step = size/10
    cdef long next_level = step - 1

    watch.reset()
    if func_hook is not None:
        for index in range(size):
            record.set_all(key, key, index, index == last_index)
            key += 1
            if not func(record):
                failed_counter += 1
            if index >= next_level:
                func_hook(theme, record, index, context)
                next_level += step
    else:
        for index in range(size):
            record.set_all(key, key, index, index == last_index)
            key += 1
            if not func(record):
                failed_counter += 1
    watch.stop()
    return failed_counter
