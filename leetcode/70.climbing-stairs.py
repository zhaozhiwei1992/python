#
# @lc app=leetcode id=70 lang=python3
# https://leetcode.com/problems/climbing-stairs/discuss/25296/3-4-short-lines-in-every-language
# [70] Climbing Stairs
# 需要找规律:   给定值计算方式有几种
#  1 : 1  1
#  2:  1+1, 2  2
#  3: 1+1+1  1+2  2+1   3种
#  4: 1+1+1+1   1+2+1  1+1+2  2+1+1  2+2   5种
#  同理 第五项应该有８种, 证号满足fibonacci 的计算方式，　每一项为前两项之和, 路径条数变成了求fibonacci 的项
#  0, 1, (前两项不算) 1, 2, 3, 5, 8, 13
class Solution:
    def climbStairs(self, n: int) -> int:
        a = b = 1
        for _ in range(n):
            # b记录累加,第一次计算第二次给a
            a, b = b, a + b
            # print(a, b)
        return a


if __name__ == '__main__':
    print(Solution().climbStairs(4))
