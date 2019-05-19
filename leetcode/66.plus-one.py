#
# @lc app=leetcode id=66 lang=python3
#
# [66] Plus One
#
class Solution:
    def plusOne(self, digits: List[int]) -> List[int]:
         digitsStr=[str(x) for x in digits]
         digitInt = int(''.join(digitsStr))+1
         return [int(x) for x in list(str(digitInt))]

