# -*- coding:utf-8 -*-
import heapq
# 维护一个队列不支持多线程
class PriorityQueue:
    def __init__(self):
        self._queue=[]
        self._index=0
    def push(self, item, priority):
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1
    def pop(self):
        #  这里插进去的是元组，所以最后一位才是属性
        return heapq.heappop(self._queue)[-1]

class Item:
    def __init__(self, name):
        self.name=name
    def __repr__(self):
        return 'Item({!r})'.format(self.name)
if __name__ == "__main__":
    q = PriorityQueue()
    q.push(Item('zhangsan'), 5)
    q.push(Item('lisi'), 6)
    q.push(Item('wangwu'), 1)
    q.push(Item('zhaoliu'), 2)
    q.push(Item('maqi'), 1)

    for i in range(4):
        print(q.pop())