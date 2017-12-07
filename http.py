# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
from db_bench import DbConnection, multi_process_bench, Options, Option
import urllib, urllib2, requests


class HttpBenchmark(DbConnection):
    def __init__(self, options):
        super(HttpBenchmark, self).__init__(options)
        self.__sess = None
        uri = options.get("uri", None)
        if uri:
            self._uri = uri
        else:
            self._uri = "http://%s:%d/%s" % (options.get("host"), options.get("port"), options.get("path"))
        self._answer_prefix = options.get("answer_prefix")

    def disconnect(self):
        pass

    def connect(self):
        pass

    # @DbConnection.benchmark()
    def urllib(self, record):
        rsp = urllib.urlopen(self._uri)
        return rsp.read().startswith(self._answer_prefix)

    @DbConnection.benchmark()
    def urllib2(self, record):
        rsp = urllib2.urlopen(self._uri)
        return rsp.read().startswith(self._answer_prefix)

    # @DbConnection.benchmark()
    def request(self, record):
        rsp = requests.get(self._uri)
        return rsp.text.startswith(self._answer_prefix)


if __name__ == "__main__":
    options = list(Options.options)
    options.append(Option('path', "P", ""))
    options.append(Option('answer_prefix', "a", None, mandatory=True))
    options.append(Option('uri', "u", None, help=u"设置后，优先使用"))
    option = Options(options)
    option.set("port", 8001)
    if option.parse_option() is False:
        exit(100)
    print(option)
    multi_process_bench(option, HttpBenchmark)
