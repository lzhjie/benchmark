# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import sys


def string2bool(s):
    return s.lower() == "true"


def string2int(s):
    return int(s)


def string2string(s):
    return str(s)


def read_file_data(s):
    with open(s) as fp:
        return fp.read()
    return None


def empty(s):
    return s


class Option:
    def __init__(self, name, short_name, default, conv=None, mandatory=False, help=None):
        if conv is None:
            if default is None:
                conv = empty
            elif type(default) == int :
                conv = string2int
            elif type(default) == bool :
                conv = string2bool
            else:
                conv = string2string
        if help and sys.version_info.major == 2:
            help = help.encode("utf-8")
        self.__info = (name, short_name, default, conv, help, mandatory)

    @property
    def name(self):
        return self.__info[0]

    @property
    def short_name(self):
        return self.__info[1]

    @property
    def default(self):
        return self.__info[2]

    @property
    def conv(self):
        return self.__info[3]

    @property
    def help(self):
        return self.__info[4]

    @property
    def mandatory(self):
        return self.__info[5]


class Options(object):
    def __init__(self, options, args=None):
        if options is None:
            raise Exception("options is None")
        self._args =args if args else sys.argv
        self.options = options
        self.__name = {item.name: item for item in options}
        self.__short_name = {item.short_name: item for item in options}
        self.__require = [item for item in options if item.mandatory]
        # conflict check
        assert len(self.__name) == len(options)
        assert len(self.__short_name) == len(options)
        self.__values = {}

    def parse_option(self, raise_when_fail=False):
        ret = self._parse_option()
        if ret is False and raise_when_fail is True:
            print(self.usage() + self.help())
            raise RuntimeError()
        return ret

    def set(self, name, value):
        self.__values[name] = value

    def get(self, name, default=None):
        value = self.__values.get(name)
        if value is not None:
            return value
        if default is not None:
            return default
        option = self.__name.get(name, None)
        return None if option is None else option.default

    def items(self):
        return [(item.name,self.get(item.name)) for item in self.options]

    def usage(self):
        temp = "Usage: python " + self._args[0]
        options = sorted(self.options, key=lambda x: 0 if x.mandatory else 1)
        for option in options:
            if option.mandatory:
                temp += " -%s %s" % (option.short_name, option.name)
            else:
                temp += " [-%s %s]" % (option.short_name, option.name)
        if self.__name.get("help") is None:
            temp += " [--help]"
        temp += "\r\n"
        return temp

    def help(self):
        help = "parameters:\r\n"
        options = sorted(self.options, key=lambda x: 0 if x.mandatory else 1)
        help_items = [("parameter", "help")]
        for x in options:
            require = "<M>" if x.mandatory else "<O>"
            name = "--%s (-%s) %s" % (x.name, x.short_name, require)
            help_c = "" if x.help is None else x.help
            if x.default is not None:
                help_c += "<%s>" % x.default
            help_items.append((name, help_c))
        try:
            from texttable import Texttable
            table = Texttable()
            table.set_deco(Texttable.HEADER|Texttable.BORDER)
            table.set_cols_dtype(['t', 't'])
            table.set_cols_align(["r", "l"])
            table.add_rows(help_items)
            help += table.draw()
        except:
            print("no module: texttable")
            for k, v in help_items:
                help += "{name:>24}: {help:<}\r\n".format(name=k, help=v)
        return help

    def _parse_option(self):
        i = 1
        while i < len(self._args):
            cur_arg = self._args[i]
            i += 1
            if cur_arg.startswith("--"):
                k, v = (cur_arg[2:] + "=").split("=")[:2]
                option = self.__name.get(k, None)
                if option:
                    if v is None or len(v) == 0:
                        self.__values[option.name] = option.default
                        continue
                else:
                    if k == "help":
                        print(self.usage() + self.help())
                        exit(0)
            elif cur_arg.startswith("-"):
                k = cur_arg[1:]
                if i >= len(self._args):
                    return False
                v = self._args[i]
                i += 1
                option = self.__short_name.get(k, None)
            else:
                return False
            if option is None:
                return False
            self.__values[option.name] = option.conv(v)
        for item in self.__require:
            if self.__values.get(item.name, None) is None:
                print("%s is required" % item.name)
                return False
        return True

    def __getitem__(self, item):
        return self.__values[item]

    def __str__(self):
        temp = "values:\r\n"
        for k,v in self.__values.items():
            temp += "%s: %s\r\n" % (k, v)
        return temp


def example():
    options = (
        Option("host", "h", "127.0.0.1", mandatory=True),
        Option("port", "p", 0, help="port "*20),
        Option("quiet", "q", False, conv=string2bool),
        Option("prefix_redirect", "pd", None,
               help="The protocol and server name to use in URLs, e.g.\r\n"       
                    "http://en.wikipedia.org. This is sometimes necessary because server name"
                    "detection may fail in command line scripts."),
        )
    option = Options(options)
    if option.parse_option() is False:
        print(option.usage() + option.help())
    print(option)
    print(option["host"])
    print(option["host_error"])

if __name__ == "__main__":
    example()