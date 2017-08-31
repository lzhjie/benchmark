# Copyright (C) zhongjie luo <l.zhjie@qq.com>
# coding: utf-8
import datetime


class StopWatch:
    def __init__(self):
        self.__start = datetime.datetime.now()

    def time(self):
        return str(datetime.datetime.now() - self.__start)

    def reset(self):
        self.__start = datetime.datetime.now()

    def seconds(self):
        delta = datetime.datetime.now() - self.__start
        return "%d.%03d" % (delta.seconds, delta.microseconds / 1000)

    def seconds_float(self):
        delta = datetime.datetime.now() - self.__start
        return delta.total_seconds()

    def seconds_int(self):
        delta = datetime.datetime.now() - self.__start
        return delta.seconds

if __name__ == "__main__":
    import time
    watch = StopWatch()
    time.sleep(1)
    print(watch.time())