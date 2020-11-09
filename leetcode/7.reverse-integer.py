#
# @lc app=leetcode id=7 lang=python3
#
# [7] Reverse Integer
#
# https://leetcode.com/problems/reverse-integer/description/
#
# algorithms
# Easy (25.22%)
# Total Accepted:    644.2K
# Total Submissions: 2.6M
# Testcase Example:  '123'
#
# Given a 32-bit signed integer, reverse digits of an integer.
# 
# Example 1:
# 
# 
# Input: 123
# Output: 321
# 
# 
# Example 2:
# 
# 
# Input: -123
# Output: -321
# 
# 
# Example 3:
# 
# 
# Input: 120
# Output: 21
# 
# 
# Note:
# Assume we are dealing with an environment which could only store integers
# within the 32-bit signed integer range: [−2^31,  2^31 − 1]. For the purpose
# of this problem, assume that your function returns 0 when the reversed
# integer overflows.
# 
#
class Solution:
    def reverse(self, x: int) -> int:
        maxint = 2<<30
        minint = -2<<30
        if(x > maxint or (x <= minint)):
            return 0
        # 转字符串
        s = str(abs(x)) 
        # 反转并int化
        i = int(s[::-1]) 
        if(x > 0 and i <= maxint):
            return i
        elif(x < 0 and (0-i) >= minint):
            return 0-i
        else:
            return 0
if __name__ == "__main__":
    solution = Solution()
    result =solution.reverse(123)
    print(result)