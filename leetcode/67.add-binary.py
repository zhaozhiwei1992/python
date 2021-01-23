#
# @lc app=leetcode id=67 lang=python3
#
# [67] Add Binary
#
class Solution:
    def addBinary(self, a: str, b: str) -> str:
        #  输入转成二进制正数求和相加在转二进制
        # bin后去掉前两位就是结果
        return bin(int(a, 2) + int(b, 2))[2:]


if __name__ == '__main__':
    print(Solution().addBinary("11", "10"))
    # print(int("11", 2))
    # print(bin(5))
