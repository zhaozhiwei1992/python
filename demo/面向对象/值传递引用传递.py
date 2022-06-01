#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class A:
    def __init__(self, value):
        self.value = value

    def toString(self):
        print("我是%s, 我的地址 %s", (self.value, id(self)))


class B:
    def __init__(self, value):
        self.value = value

    def toString(self):
        print("我是%s, 我的地址 %s", (self.value, id(self)))


def change(o):
    print("传入形参改变前的地址", id(o))
    o = B("B")
    o.toString()


if __name__ == '__main__':
    # 定义一个a
    a = A("A")

#    通过方法传递
    change(a)

    a.toString()
