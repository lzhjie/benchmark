# Copyright (C) zhongjie luo <l.zhjie@qq.com>
# coding: utf-8
import sys
if sys.version.startswith("3"):
    from .StopWatch import StopWatch
    from .ColorPrint import ColorPrint
else:
    from StopWatch import StopWatch
    from ColorPrint import ColorPrint

class ProgressBar:
    # interval: 1-100
    def __init__(self, max_value, title="", interval_val=10, interval_sec=0.5, width=50, char='>'):
        if interval_val < 1 or interval_val > 100:
            self.__interval = 10
        else:
            self.__interval = interval_val
        self.__width = width if width > 0 else 50
        self.__interval_value = max_value / interval_val
        if self.__interval_value <= 0:
            self.__interval_value = 1
        self.__max_value = max_value
        self.__next_print_value = self.__interval_value
        self.__c = ord(char)
        self.__watch = StopWatch()
        self.__interval_sec = interval_sec
        self.__next_print_sec = self.__interval_sec
        self.__counter = 0
        self.__title = title
        self.__is_finished = False

    def reset(self):
        self.__is_finished = False
        self.__next_print_value = self.__interval_value
        self.__next_print_sec = self.__interval_sec
        self.__counter = 0
        self.__watch.reset()

    def check(self, cur_value):
        """invoke print if return True"""
        if cur_value == 0:
            return True
        if cur_value < self.__next_print_value:
            return False
        if self.__is_finished:
            return False
        if cur_value >= self.__max_value:
            return True
        if self.__watch.seconds_float() < self.__next_print_sec:
            self.__to_next_state(cur_value, False)
            return False
        return True

    # finished return True
    def print_bar(self):
        self.__counter += 1
        return self.print_bar_by_value(self.__counter)

    def print_bar_by_value(self, cur_value):
        if self.check(cur_value) is True:
            sys.stdout.write("\r" + self.bar_string(cur_value))
            sys.stdout.flush()
        if self.is_finished():
            sys.stdout.write("\n")
            return True
        return False

    def bar_string(self, value, title=None):
        pos = value * 100 / self.__max_value
        cost = self.__watch.seconds()
        fill = self.__width
        if pos < 100:
            self.__to_next_state(value)
            fill = int(self.__width * pos / 100)
        else:
            self.__is_finished = True
        b_str = bytearray(' ' * self.__width, "utf-8")
        c = self.__c
        for i in range(fill):
            b_str[i] = c
        if title is None:
            title = self.__title
        bar = "%s [%s] %d%% %ss                   " % \
              (title, b_str.decode(), pos * 100 / 100, cost)
        return bar

    def is_finished(self):
        return self.__is_finished

    def __to_next_state(self, cur_value, update_time = True):
        self.__next_print_value = cur_value + self.__interval_value
        if self.__next_print_value > self.__max_value:
            self.__next_print_value = self.__max_value
        if update_time:
            self.__next_print_sec = self.__watch.seconds_float() + self.__interval_sec


class MultiBar:
    def __init__(self, color=None):
        self.__color = color
        self.__bars = []
        self.__last_id = 0

    def append_bar(self, bar):
        if not isinstance(bar, ProgressBar):
            raise TypeError("require ProgressBar instance")
        index = len(self.__bars)
        self.__bars.append(bar)
        self.print_bar(index, 0)
        return index

    def check(self, index, value):
        bar = self.__bars[index]
        return bar.check(value)

    def print_bar(self, index, value, title=None):
        bar = self.__bars[index]
        if bar.check(value) is True:
            buffer = bytearray()
            self.__cursor_to_line(index, buffer)
            buffer.append(ord('\r'))
            temp = bar.bar_string(value, title)
            if bar.is_finished() and self.__color:
                temp = self.__color.to_color(temp)
            buffer += bytearray(temp, "utf-8")
            self.__to_tail_line(buffer)
            sys.stdout.write(buffer.decode())
            sys.stdout.flush()
            return True
        return False

    def reset(self, index=None):
        if id is not None:
            if index < 0 or index >= len(self.__bars):
                return
            self.__bars[index].reset()
        else:
            self.__last_id = 0
            for bar in self.__bars:
                bar.reset()

    def __len__(self):
        return len(self.__bars)

    def __cursor_to_line(self, id, buffer=None):
        temp = bytearray()
        if self.__last_id > id:
            temp += bytearray("\x1b[%dA" % (self.__last_id - id), "utf-8")
        elif self.__last_id < id:
            temp += bytearray("\r\n" * (id - self.__last_id), "utf-8")
        else:
            return
        self.__last_id = id
        if buffer is not None:
            buffer += temp
        else:
            sys.stdout.write(temp.decode())
            sys.stdout.flush()

    def __to_tail_line(self, buffer=None):
        """for multiprocessing"""
        self.__cursor_to_line(len(self.__bars), buffer)


def example_bar():
    import time
    bar = ProgressBar(100, "test")
    for i in range(100):
        if bar.print_bar_by_value(i) is True:
            break
        time.sleep(0.05)
    bar.reset()
    for i in range(100):
        if bar.print_bar() is True:
            break
        time.sleep(0.05)


def example_multibar():
    """windows did not deal with \b"""
    import time
    mbar = MultiBar(color=ColorPrint(36))
    bar_size = 2
    for i in range(bar_size):
        mbar.append_bar(ProgressBar(100, "test" + str(i)))
    for i in range(100):
        mbar.print_bar(i % 7, i)
        time.sleep(0.05)
    for i in range(bar_size):
        mbar.print_bar(i, 100)

    for i in range(bar_size):
        mbar.reset(i)
    for i in range(100):
        mbar.print_bar(i % 7, i, str(i) + "title new")
        time.sleep(0.05)


if __name__ == "__main__":
    # example_bar()
    example_multibar()
