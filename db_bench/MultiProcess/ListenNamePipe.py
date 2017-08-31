# Copyright (C) zhongjie luo <l.zhjie@qq.com>
# named pipe Server
# encoding: utf-8

import os
import select


class ListenNamedPipe:
    def __init__(self, name, func, context):
        try:
            os.mkfifo(name)
        except OSError as e:
            print "mkfifo error:", e
            raise e
        self.__name = name
        self.__func = func
        self.__context = context
        self.__running = False

    def __del__(self):
        os.remove(self.__name)

    def listen(self):
        if self.__running:
            return
        rf = open(self.__name, "r")
        epoll = select.epoll()
        epoll.register(rf, select.EPOLLIN |select.EPOLLET)
        self.__running = True
        while self.__running:
            epoll_list = epoll.poll(1)
            if not epoll_list:
                continue
            if epoll_list[0][1] & select.EPOLLERR:
                print "EPOLLERR ", self.__name
                return
            s = rf.read()
            if self.__func(s, self.__context) is False:
                break

    def stop(self):
        if self.__running:
            self.__running = False