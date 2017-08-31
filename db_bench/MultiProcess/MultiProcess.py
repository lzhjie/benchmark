# Copyright (C) zhongjie luo <l.zhjie@qq.com>
# coding: utf-8
from multiprocessing import cpu_count, Process, Queue
import os, re, datetime, sys, signal


class StopWatch:
    def __init__(self):
        self.__start = datetime.datetime.now()

    def time(self):
        return str(datetime.datetime.now() - self.__start)

    def reset(self):
        self.__start = datetime.datetime.now()


def find_files(dir, pattarn, recursion=False):
    result = []
    patt = re.compile(pattarn)
    for root, subdirs, files in os.walk(dir):
        for name in files:
            if patt.match(name) is not None:
                full_name = os.path.join(root, name)
                result.append(full_name)
        if not recursion:
            break
    return result


def file_size(filename):
    size = os.path.getsize(filename)
    return "%.2fM" % (size / 1024 / 1024)


class MsgProcess(Process):
    def __init__(self, master_queue, id, func, context):
        super(MsgProcess, self).__init__()
        self.__func = func
        self.__is_running = False
        self.__context = context
        self.__queue = Queue()
        self.__master_queue = master_queue
        self.__id = id

    def __del__(self):
        self.stop()
        self.join()

    def id(self):
        return self.__id

    def put_msg(self, msg):
        self.__queue.put(msg, True)
        #print "put ", msg, self.pid, self.__queue.empty()

    def start(self):
        if not self.__is_running:
            self.__is_running = True
            super(MsgProcess, self).start()

    def stop(self):
        if self.__is_running:
            self.__is_running = False
            self.put_msg("\0")

    def join(self):
        super(MsgProcess, self).join()

    def run(self):
        signal.signal(signal.SIGTERM, self.stop)
        while self.__is_running:
            msg = self.__queue.get(True)
            #print os.getpid(), "get", msg
            if msg == "\0":
                self.__is_running = False
                break;
            try:
                self.__func(msg, self.__context)
            except:
                print(str(sys.exc_info()))
                print("EXCEPTION message: " + str(msg))
            if self.__queue.empty():
                self.__master_queue.put(self.id(), True)


class MsgProcessPool:
    def __init__(self, num, func, context, force=False):
        if num > cpu_count() and force is False:
            num = cpu_count()
            print("change num to " + str(num))
        self.__num = num if num > 0 else 1
        self.__seq = 0
        self.__q = Queue()
        self.__pool = [MsgProcess(self.__q, i, func, context) for i in range(num)]
        for x in self.__pool:
            self.__q.put(x.id())

    def __del__(self):
        self.stop()

    def get_free_process(self, timeout):
        try:
            free_id = self.__q.get(True, timeout)
            return self.__pool[free_id]
        except:
            return None

    def process_msg(self, msg, timeout):
        process = self.get_free_process(timeout)
        if process is None:
            print("timeout, msg: " + msg)
            return False
        # 发送int(0) 失败， 只处理str类型
        process.put_msg(str(msg))
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


class FileInfo:
    def __init__(self, name, id):
        self.__name = name
        self.__id = id
        size = float(os.path.getsize(name))
        self.__str = "(%s) %s %.3fM" % (self.__id, self.__name, size / 1024 / 1024)

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id

    def __str__(self):
        return self.__str


class MultiProcess:
    def __init__(self, process_num, func, context=None, force=False):
        self.__pool = MsgProcessPool(process_num, func, context, force)
        self.__cost = "--"
        self.__watch = StopWatch()
        self.__pool.start()

    def __del__(self):
        self.__pool.stop()

    def join(self):
        self.__pool.stop()
        self.__cost = self.__watch.time()

    def cost(self):
        return self.__cost

    def process_msg(self, msg, timeout=None):
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
    print("cost: ", process.cost())


if __name__ == "__main__":
    example()
