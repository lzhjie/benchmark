# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import datetime


class StopWatch:
    def __init__(self):
        self.__start = datetime.datetime.now()
        self.__stop = None

    def stop(self):
        self.__stop = datetime.datetime.now()

    def reset(self):
        self.__start = datetime.datetime.now()
        self.__stop = None

    def __cur_time(self):
        return self.__stop if self.__stop else datetime.datetime.now()

    def time(self):
        return str(self.__cur_time() - self.__start)

    def seconds(self):
        delta = self.__cur_time() - self.__start
        return "%d.%03d" % (delta.seconds, delta.microseconds / 1000)

    def seconds_float(self):
        delta = self.__cur_time() - self.__start
        return delta.total_seconds()

    def seconds_int(self):
        delta = self.__cur_time() - self.__start
        return delta.seconds


if __name__ == "__main__":
    import time

    watch = StopWatch()
    time.sleep(1)
    print(watch.time())
