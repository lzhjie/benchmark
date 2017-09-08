# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>


class ColorPrint:
    """
    字体色 | 背景色 | 颜色描述
    -------------------------------------------
    30 | 40 | 黑色
    31 | 41 | 红色
    32 | 42 | 绿色
    33 | 43 | 黃色
    34 | 44 | 蓝色
    35 | 45 | 紫红色
    36 | 46 | 青蓝色
    37 | 47 | 白色
    -------------------------------------------
    -------------------------------
    显示方式 | 效果
    -------------------------------
    0 | 终端默认设置
    1 | 高亮显示
    4 | 使用下划线
    5 | 闪烁
    7 | 反白显示
    8 | 不可见
    -------------------------------
    """
    reset = "\x1b[0m"

    def __init__(self, color=30, bg_color=None, style=None):
        self.__color = "\x1b["
        if style:
            self.__color += "%d;" % style
        if bg_color:
            self.__color += "%d;" % bg_color
        self.__color += "%dm" % color

    def to_color(self, str):
        return "%s%s%s" % (self.__color, str, ColorPrint.reset)

    def print_str(self, str):
        print(self.to_color(str))


if __name__ == "__main__":
    color = ColorPrint(32, 40, 1)
    color.print_str("test")
