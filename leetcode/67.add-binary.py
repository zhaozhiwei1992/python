#
# @lc app=leetcode id=67 lang=python3
#
# [67] Add Binary
#
class Solution:
    def addBinary(self, a: str, b: str) -> str:
        #  输入转成二进制正数求和相加在转二进制
        return bin(int(a,2)+int(b,2))[2:] 

