# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>

from multiprocessing import cpu_count, Process, Queue
import os
import traceback


class MsgProcess(Process):
    def __init__(self, master_queue, id, func, context):
        super(MsgProcess, self).__init__()
        self.__func = func
        self.__is_running = False
        self.__context = context
        self.__queue = Queue()
        self.__master_queue = master_queue
        self.__id = id

    def id(self):
        return self.__id

    def put_msg(self, msg):
        self.__queue.put(msg, True)
        # print "put ", msg, self.pid, self.__queue.empty()

    def start(self):
        if not self.__is_running:
            self.__is_running = True
            super(MsgProcess, self).start()

    def stop(self):
        if self.__is_running:
            self.__is_running = False
            self.put_msg(None)

    def join(self):
        super(MsgProcess, self).join()

    def run(self):
        __func_queue_get = self.__queue.get
        __func_process_msg = self.__func
        while self.__is_running:
            self.__master_queue.put(self.id(), True)
            msg = __func_queue_get(True)
            if msg is None:
                self.__is_running = False
                break;
            try:
                __func_process_msg(msg, self.__context)
            except (SystemExit, KeyboardInterrupt):
                print("exit, pid %d" % os.getpid())
                return
            except:
                traceback.print_exc()
                print("EXCEPTION message: " + str(msg))


class MsgProcessPool:
    def __init__(self, num, func, context, force=False, buffer_size=0):
        if num > cpu_count() and force is False:
            num = cpu_count()
            print("change num to " + str(num))
        self.__num = num if num > 0 else 1
        self.__seq = 0
        self.__q = Queue()
        self.__pool = [MsgProcess(self.__q, i, func, context) for i in range(num)]
        for i in range(buffer_size):
            for x in self.__pool:
                self.__q.put(x.id())

    def __del__(self):
        self.stop()

    def get_free_process(self, timeout):
        try:
            # blocked when CTRL+c if timeout is None
            free_id = self.__q.get(True, timeout)
            return self.__pool[free_id]
        except (SystemExit, KeyboardInterrupt):
            raise SystemExit()
        except:
            return None

    def process_msg(self, msg, timeout):
        process = self.get_free_process(timeout)
        if process is None:
            print("timeout, msg: " + str(msg))
            return False
        process.put_msg(msg)
        return True

    def start(self):
        for process in self.__pool:
            process.start()

    def stop(self):
        for process in self.__pool:
            process.stop()
        while len(self.__pool):
            process = self.__pool.pop(0)
            process.join()
            del process

    def num(self):
        return len(self.__pool)


class MultiProcess:
    def __init__(self, process_num, func, context=None, force=False, buffer_size=1):
        self.__pool = MsgProcessPool(process_num, func, context, force, buffer_size)
        self.__pool.start()

    def __del__(self):
        self.__pool.stop()

    def join(self):
        self.__pool.stop()

    def process_msg(self, msg, timeout=600):
        return self.__pool.process_msg(msg, timeout)

    @staticmethod
    def cpu_count():
        return cpu_count()

    @staticmethod
    def half_cpu_count():
        return (cpu_count() + 1) / 2

    def thread_num(self):
        return self.__pool.num()


def msg_func(msg, context):
    import time
    print("%s %s %s" % (str(os.getpid()), str(msg), str(context)))
    time.sleep(0.5)


def example():
    process = MultiProcess(2, msg_func, "test")
    for i in range(10):
        process.process_msg(i)
    process.join()
    print("finish")


if __name__ == "__main__":
    example()
