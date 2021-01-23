#
# @lc app=leetcode id=66 lang=python3
#
# [66] Plus One
#
from typing import List


class Solution:
    def plusOne(self, digits: List[int]) -> List[int]:
        """
        总数+1再拆分
        ['1', '2', '3']
        124
        [1, 2, 4]
        :param digits:
        :return:
        """
        digitsStr = [str(x) for x in digits]
        # print(digitsStr)
        digitInt = int(''.join(digitsStr)) + 1
        # print(digitInt)
        return [int(x) for x in list(str(digitInt))]


if __name__ == '__main__':
    print(Solution().plusOne([1, 2, 3]))
