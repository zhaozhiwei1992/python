#
# @lc app=leetcode id=69 lang=python
#
# [69] Sqrt(x)
#
class Solution(object):
    def mySqrt(self, x):
        """
        :type x: int
        :rtype: int
        """
        #  参考 https://www.runoob.com/python3/python3-square-root.html
        return int(x ** 0.5)


if __name__ == '__main__':
    print(Solution().mySqrt(4))
