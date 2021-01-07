#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   frenchDeck.py
@Time    :   2019/10/13 10:33:06
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib
import collections

'''
rank 数字
suit 花色

一张纸牌，两个属性 rank, suit
'''
Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck:
    '''
    纸牌盒
    单元测试
    >>> f = FrenchDeck()
    >>> len(f) 
    52
    >>> Card('7', '黑桃') in f
    True
    '''

# 一个花色拍的数字
    ranks = [str (i) for i in range(2, 11)] + list('JQKA')
# 所有的花色
    suits = '红桃 方块 梅花 黑桃'.split()

    def __init__(self, *args, **kwargs):
        # 双层循环赋值
        self._cards = [Card(rank, suit) for rank in self.ranks for suit in self.suits]

    def __len__(self):
        return len(self._cards)
    
    def __getitem__(self, position):
        return self._cards[position]

from random import choice
if __name__ == "__main__":
    '''
    python -m doctest -v unnecessary_math.py
    这里 -m 表示引用一个模块，-v 等价于 verbose=True。运行输出与上面基本一样。
    '''
    # import doctest
    # doctest.testmod()

    f = FrenchDeck()
    # print(f._cards) # 所有纸牌
    print(len(f)) # 纸牌个数
    # 任选一张
    print(choice(f))
    # 获取前三张牌
    print(f[:3])
    # 排序
    # 迭代通常是隐式的，譬如说一个集合类型没有实现 __contains__ 方法，那么 in 运算符就会按顺序做一次迭代搜索
    #这样可以做为判断黑桃七是否在纸牌中
    print(Card('7', '黑桃') in f)
