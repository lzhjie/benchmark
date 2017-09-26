# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
#-cython optimize.unpack_method_calls=False
import cython


cdef extern from "<Python.h>":
    ctypedef struct PyObject
    void Py_XINCREF(PyObject*)
    void Py_XDECREF(PyObject*)
    PyObject* PyInt_FromLong(long)
    PyObject* Py_BuildValue(const char *, ...)
    PyObject* PyTuple_New(Py_ssize_t)
    int PyTuple_SetItem(PyObject*, Py_ssize_t, PyObject*);


@cython.locals(index = long)
cpdef benchmark_cython(theme, data, watch, func, func_hook, context):
    data.reset()
    cdef long failed_counter = 0
    cdef long size = len(data)
    cdef long last_index = size - 1
    cdef long key = data.range_l
    cdef long step = size/10
    cdef long next_level = step - 1

    if func_hook is None:
        next_level = size
    record = PyTuple_New(3)
    kv = Py_BuildValue("(ii)", 0, 0)
    # tuple 必选先初始化item，否则Segmentation fault (core dumped)
    PyTuple_SetItem(record, 0, kv)
    PyTuple_SetItem(record, 1, PyInt_FromLong(0))
    PyTuple_SetItem(record, 2, PyInt_FromLong(last_index))
    watch.reset()
    for index in range(size):
        PyTuple_SetItem(record, 1, PyInt_FromLong(index))
        PyTuple_SetItem(kv, 0, PyInt_FromLong(key))
        PyTuple_SetItem(kv, 1, PyInt_FromLong(key))
        if not func(<object>record):
            failed_counter += 1
        if index >= next_level:
            func_hook(theme, <object>record, index, context)
            next_level += step
        key += 1
    watch.stop()
    Py_XDECREF(record)
    # Py_XDECREF(kv) // auto dealloc when Py_XDECREF(record)
    return failed_counter
