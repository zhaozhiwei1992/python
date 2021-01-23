#
# @lc app=leetcode id=9 lang=python3
#
# [9] Palindrome Number
#
# https://leetcode.com/problems/palindrome-number/description/
#
# algorithms
# Easy (42.52%)
# Total Accepted:    539.7K
# Total Submissions: 1.3M
# Testcase Example:  '121'
#
# Determine whether an integer is a palindrome. An integer is a palindrome when
# it reads the same backward as forward.
# 
# Example 1:
# 
# 
# Input: 121
# Output: true
# 
# 
# Example 2:
# 
# 
# Input: -121
# Output: false
# Explanation: From left to right, it reads -121. From right to left, it
# becomes 121-. Therefore it is not a palindrome.
# 
# 
# Example 3:
# 
# 
# Input: 10
# Output: false
# Explanation: Reads 01 from right to left. Therefore it is not a palindrome.
# 
# 
# Follow up:
# 
# Coud you solve it without converting the integer to a string?
# 
#
"""
判断数字是否为回文
1. 小于0的肯定不是
2. 数字转字符串，倒序排列如果相等则是回文
"""


class Solution:
    def isPalindrome(self, x: int) -> bool:
        if (x < 0):
            return False
        return int(str(x)[::-1]) == x


if __name__ == "__main__":
    solution = Solution()
    print("是否回文数: %s" % solution.isPalindrome(121))
