# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import datetime, random, os, sys, copy, json

if sys.version_info.major >= 3:
    from .tools.StopWatch import StopWatch
    from .tools.ProgressBar import ProgressBar, MultiBar
    from .tools.ColorPrint import ColorPrint
    from .tools.MultiProcess import MultiProcess
    from .tools.Options import Options as toolsOptions, Option, string2bool
else:
    from tools.StopWatch import StopWatch
    from tools.ProgressBar import ProgressBar, MultiBar
    from tools.ColorPrint import ColorPrint
    from tools.MultiProcess import MultiProcess
    from tools.Options import Options as toolsOptions, Option, string2bool

from multiprocessing import Lock, Queue, Semaphore


class Options(toolsOptions):
    options = (
        Option("host", "h", "127.0.0.1"),
        Option("port", "p", 0),
        Option("processor_num", "n", 1),
        Option("record_num", "r", 1000),
        Option("processor_num_max", "n_max", 50),
        Option("record_num_max", "r_max", 10000000),
        Option("out_dir", "d", "result"),
        Option("tag", "t", "tag",
               help=u"添加到输出文件名中，可用于区分同类型测试\r\n" \
                    u"例如用时间来命名每次测试结果的输出文件\r\n"),
        Option("table", "T", "__benchmark"),
        Option("key_start", "k", 10000),
        Option("quiet", "q", False, string2bool))

    def __init__(self, options=None, args=None):
        if options is None:
            options = Options.options
        super(Options, self).__init__(options, args)

    def parse_option(self, raise_when_fail=False):
        if super(Options, self).parse_option(raise_when_fail) is False:
            print(self.usage() + self.help())
            return False
        return True


class DbConnection(object):
    """type(record)->((k, v), index, last_index)"""
    _benchmark_funcs = {}

    def __init__(self, options):
        self.name = options.get("_name")
        self.host = options.get("host")
        self.port = options.get("port")
        self.table = options.get("table")
        self.id = options.get("_id")
        self.quiet = options.get("quiet")
        self.record_num = options.get("_count_per_processor")
        self.options = options
        self._benchmark_funcs = {}
        default_funcs = ("insert", "search", "update", "delete")
        for func_name in default_funcs:
            func = getattr(self, func_name, None)
            func_self = getattr(DbConnection, func_name, None)
            if getattr(func, "__code__") != getattr(func_self, "__code__"):
                self._benchmark_funcs[func.__name__] = func
        for func in self.__class__.__dict__.values():
            if getattr(func, "benchmark", None) is True:
                self._benchmark_funcs[func.__name__] = getattr(self, func.__name__)

    @staticmethod
    def benchmark(label=None):
        """:param name, for echarts label"""

        def _benchmark(func):
            func.benchmark = True
            func.label = label
            return func

        return _benchmark

    def benchmark_funcs(self):
        """benchmark_funcs()->{func_name: func}"""
        return self._benchmark_funcs

    def connect(self):
        raise NotImplemented

    def disconnect(self):
        raise NotImplemented

    def insert(self, record):
        raise NotImplemented

    def search(self, record):
        raise NotImplemented

    def update(self, record):
        raise NotImplemented

    def delete(self, record):
        raise NotImplemented

    def set_up(self):
        """invoke before benchmark"""
        raise NotImplemented

    def tear_down(self):
        """invoke after benchmark"""
        raise NotImplemented

    def _warm_up(self, record):
        (k, v), index, last_index = record
        return True

    def __str__(self):
        return "%d %s[%s] %s:%s" % \
               (self.id, self.name, self.table, self.host, self.port)


class Record(object):
    def __init__(self, key, value, id=0, is_tail=False):
        self.__record = (key, value, id, is_tail)

    def key(self):
        return self.__record[0]

    def value(self):
        return self.__record[1]

    def id(self):
        return self.__record[2]

    def is_tail(self):
        return self.__record[3]

    def set_all(self, all):
        self.__record = all


class Data(object):
    def __init__(self, size, range_l=10000, options=None):
        self.__size = int(size)
        self.size = int(size)
        self.range_l = int(range_l)
        self.options = options
        self.__cursor = int(0)
        self.reset()

    def hook_get_item(self, index):
        return None

    def hook_reset(self):
        pass

    def reset(self):
        self.__cursor = 0
        self.hook_reset()

    def hook_get_key_and_value(self, index):
        return (None, None)

    def next(self):
        if self.__cursor >= self.__size:
            raise StopIteration()
        item = self.hook_get_item(self.__cursor)
        self.__cursor += 1
        return item

    def __next__(self):
        return self.next()

    def __len__(self):
        return self.__size

    def __iter__(self):
        return self


class DataRecord(Data):
    def __init__(self, size, range_l=10000, options=None):
        super(DataRecord, self).__init__(size, range_l, options)
        self.__record = Record("Null", "Null")

    def hook_get_item(self, index):
        k, v = self.hook_get_key_and_value(index)
        self.__record.set_all((k, v, index, index + 1 == self.size))
        return self.__record

    def hook_get_key_and_value(self, index):
        key = str(index + self.range_l)
        return (key, key)


class DataRandom(DataRecord):
    def __init__(self, size, range_l=10000, options=None):
        self.__seed = range_l + size
        self.__range_l = range_l
        self.__range_r = range_l + size * 10
        self.__value = str(datetime.datetime.now()) + " "
        super(DataRandom, self).__init__(size, range_l, options)

    def hook_get_key_and_value(self, index):
        return (str(random.randint(self.__range_l, self.__range_r)),
                self.__value + str(index))

    def hook_reset(self):
        random.seed(self.__seed)


class DataFile(DataRecord):
    def __init__(self, size, range_l=10000, options=None):
        super(DataFile, self).__init__(size, range_l, options)
        file_name = options.get("file", None)
        if file_name is None:
            raise Exception("require option file")
        with open(file_name, "r") as fp:
            self.lines = fp.readlines()
        self.size = len(self.lines)
        self.key = str(datetime.datetime.now()) + " " + str(range_l) + " "

    def hook_get_key_and_value(self, index):
        return (self.key + str(index), self.lines[index % self.size])


def benchmark(theme, data, watch, func, func_hook, context):
    failed_counter = 0
    data.reset()
    size = len(data)
    last_index = size - 1
    step = size / 10
    next_level = 0

    __func_get_kv = data.hook_get_key_and_value
    __func_hook = func_hook
    __context = context
    watch.reset()
    if __func_hook is not None:
        for index in range(size):
            kv = __func_get_kv(index)
            record = (kv, index, last_index)
            if not func(record):
                failed_counter += 1
            if index >= next_level:
                __func_hook(theme, record, __context)
                next_level += step
                if next_level > last_index:
                    next_level = last_index
    else:
        for index in range(size):
            kv = __func_get_kv(index)
            if not func((kv, index, last_index)):
                failed_counter += 1
    watch.stop()
    return failed_counter


class DbBench:
    def __init__(self, connection, data, hook_func=None, context=None):
        if not issubclass(type(connection), DbConnection):
            raise TypeError("param 1 must be a instance of DbConnection's subclass ")
        if not issubclass(type(data), Data):
            raise TypeError("param 2 must be a instance of Data's subclass ")
        self.__connected = False
        self.conn = connection
        self.conn.connect()
        self.__connected = True
        self.data = data
        self.__hook_func = hook_func
        self.__result = {}
        self.__context = context
        self.__warm_up = False

    def __del__(self):
        if self.__connected:
            self.conn.disconnect()

    def get_result(self):
        return self.__result

    def __test_func(self, func, theme):
        watch = StopWatch()
        __benchmark = benchmark
        m = sys.modules.get('db_bench.DbBench', None)
        if m and m.__file__.endswith(".so") and DataRecord == self.data.__class__:
            import importlib
            temp = importlib.import_module("db_bench.DbBenchCython")
            __benchmark = temp.benchmark_cython

        # warm up
        if self.__warm_up is False:
            self.__warm_up = True
            __benchmark("warmup", self.data, watch, self.conn._warm_up, self.__hook_func, self.__context)

        failed_counter = __benchmark(theme, self.data, watch, func, self.__hook_func, self.__context)

        cost = max(float("%.3f" % watch.seconds_float()), 0.001)
        self.__result[theme] = {}
        stat = self.__result[theme]
        size = len(self.data)
        stat["label"] = getattr(func, "label", theme)
        stat["sum"] = size
        stat["cost"] = cost
        stat["qps"] = float("%.3f" % (size / cost))
        stat["fail"] = failed_counter

    def benchmark(self):
        funcs = self.conn.benchmark_funcs()
        for name, func in funcs.items():
            self.__test_func(func, name)


def process_func(msg, context):
    id = int(msg)
    multi_bar = context["bar"]
    options = context["options"]
    options.set("_id", id)

    def progress_bar(theme, record, context):
        bar, bar_index = context
        cur_index, last_index = record[1:]
        if bar.check(bar_index, cur_index + 1):
            bar.print_bar(bar_index, cur_index + 1, "%d %s" % (bar_index + 1, theme))
            if cur_index == last_index:
                bar.reset(bar_index)

    data_count = context["data_count"]
    key_start = options.get("key_start")
    data = context["data_class"](data_count, key_start + id * data_count, options)
    bar_index = id - 1
    semaphore = context["semaphore"]
    queue_startline = context["queue_startline"]
    conn_c = context["connection_class"]
    connection = conn_c(options)
    try:
        if options.get("quiet") is True:
            db_bench = DbBench(connection, data)
        else:
            db_bench = DbBench(connection, data,
                               hook_func=progress_bar, context=(multi_bar, bar_index))
            multi_bar.reset(id)
        queue_startline.put(id)
        semaphore.acquire()
        db_bench.benchmark()
        context["queue"].put(db_bench.get_result(), True)
    finally:
        if db_bench:
            del db_bench
        del data
        del connection


def multi_process_bench(options, connection_class, data_class=DataRecord):
    if not isinstance(options, Options):
        raise TypeError("param options must be a instance of Options")
    if not issubclass(connection_class, DbConnection):
        raise TypeError("param connection_class must be DbConnection's subclass ")
    if not issubclass(data_class, Data):
        raise TypeError("param data_class must be Data's subclass ")
    processor_num = options.get("processor_num")
    processor_num_max = options.get("processor_num_max")
    record_num = options.get("record_num")
    record_num_max = options.get("record_num_max")

    if processor_num > processor_num_max:
        processor_num = processor_num_max
        print("processor_num to %d" % processor_num)
    if record_num > record_num_max:
        record_num = record_num_max
        print ("change record_num to %d" % record_num)

    count_per_processor = int(record_num / processor_num)
    if count_per_processor <= 0:
        print("count_per_processor is 0")
        return
    options.set("_id", 0)

    def clear(func):
        hook = connection_class.__dict__.get(func, None)
        if hook is not None:
            print("%s..." % func)
            conn = connection_class(options)
            conn.connect()
            hook(conn)
            conn.disconnect()

    clear("set_up")
    quiet = options.get("quiet")
    if quiet:
        bar = None
    else:
        bar = MultiBar(color=ColorPrint(36))
        for i in range(processor_num):
            bar.append_bar(ProgressBar(count_per_processor, "processor " + str(i)))
    queue = Queue()
    semaphore = Semaphore(processor_num)
    options.set("_name", connection_class.__dict__.get("name", connection_class.__name__))
    options.set("_count_per_processor", count_per_processor)
    queue_startline = Queue()
    context = {
        "data_class": data_class,
        "connection_class": connection_class,
        "data_count": count_per_processor,
        "bar": bar,
        "lock": Lock(),
        "queue": queue,
        "queue_startline": queue_startline,
        "semaphore": semaphore,
        "options": copy.deepcopy(options)
    }
    pool = MultiProcess(processor_num, process_func, context, True)
    # barrier lock
    for i in range(processor_num):
        semaphore.acquire()
    for i in range(processor_num):
        pool.process_msg(i + 1)
    for i in range(processor_num):
        queue_startline.get()
    for i in range(processor_num):
        semaphore.release()
    pool.join()
    clear("tear_down")
    result = {
        "stat": {},
        "detail": [],
        "dbinfo": {"type": options.get("_name"),
                   "host": options.get("host"),
                   "port": options.get("port"),
                   "table": options.get("table")}}
    stat = result["stat"]
    detail = result["detail"]
    try:
        for i in range(processor_num):
            msg = queue.get(True, 1)
            detail.append(copy.deepcopy(msg))
            if len(stat) == 0:
                result["stat"] = msg
                stat = result["stat"]
                continue
            for k, v in msg.items():
                target = stat[k]
                target["fail"] += v["fail"]
                target["sum"] += v["sum"]
                target["cost"] = max(target["cost"], v["cost"])
    except:
        raise RuntimeError("benchmark lost, name: " + options.get("_name"))

    if stat is not None:
        for k, v in stat.items():
            v["qps"] = int(v["sum"] / v["cost"])
            print("%s %s" % (str(k), str(v)))
    out_dir = options.get("out_dir")
    if os.path.exists(out_dir) is False:
        os.mkdir(out_dir)
    with open("%s/benchmark_%s_%d_%d_%s.json" % (out_dir,
                                                 options.get("_name").replace("_", " "),
                                                 record_num,
                                                 processor_num,
                                                 options.get("tag", "tag")), "w") as fp:
        fp.write(json.dumps(result, indent=2))
    return result


class ConnectionExample(DbConnection):
    def __init__(self, options):
        super(ConnectionExample, self).__init__(options)
        self.__client = None

    def connect(self):
        self.__client = {}

    def disconnect(self):
        self.__client = None

    @DbConnection.benchmark(u"测试")
    def null(self, record):
        return True

    def insert(self, record):
        k, v = record[0]
        self.__client[k] = v
        return True

    def search(self, record):
        k, v = record[0]
        self.__client[k] = v
        return self.__client.get(k) == v

    def update(self, record):
        return self.search(record)

    def delete(self, record):
        k, v = record[0]
        return self.__client.pop(k, None) is not None

    def clear(self):
        self.__client = {}


def example():
    option = Options()
    option.set("record_num", 100000)
    option.set("processor_num", 2)
    if option.parse_option() is False:
        return
    # option.set("quiet", True)
    print(option)
    result = multi_process_bench(option, ConnectionExample)
    print(result)


if __name__ == "__main__":
    example()
