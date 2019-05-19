#
# @lc app=leetcode id=70 lang=python3
# https://leetcode.com/problems/climbing-stairs/discuss/25296/3-4-short-lines-in-every-language
# [70] Climbing Stairs
# 需要找规律:   给定值计算方式有几种
#  1 : 1  1
# 2:  1+1, 2  2
#  3: 1+1+1  1+2  2+1   3种
#  4: 1+1+1+1   1+2+1  1+1+2  2+1+1  2+2   5种
#  同理 第五项应该有８种, 证号满足fibonacci 的计算方式，　没一项为前两项之和, 路径条数变成了求fibonacci 的项
#
class Solution:
    def climbStairs(self, n: int) -> int:
        a = b = 1
        for _ in range(n):
            a, b = b, a + b
        return a
