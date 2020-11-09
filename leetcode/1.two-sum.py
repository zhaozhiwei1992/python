#
# @lc app=leetcode id=1 lang=python3
#
# [1] Two Sum
#
# https://leetcode.com/problems/two-sum/description/
#
# algorithms
# Easy (42.86%)
# Total Accepted:    1.6M
# Total Submissions: 3.8M
# Testcase Example:  '[2,7,11,15]\n9'
#
# Given an array of integers, return indices of the two numbers such that they
# add up to a specific target.
# 
# You may assume that each input would have exactly one solution, and you may
# not use the same element twice.
# 
# Example:
# 
# 
# Given nums = [2, 7, 11, 15], target = 9,
# 
# Because nums[0] + nums[1] = 2 + 7 = 9,
# return [0, 1].
# 
# 
# 
# 通過一個map記錄每個要素的下標, 這種情況下如果要素相同，用哪個都可以
# 判斷key值滿足target-element就可以返回
#
# 类型要引入，否则方法注释不可用
from typing import List

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        dict = {}
        for index, ele in enumerate(nums):
            if dict.keys().__contains__(target - ele):
                return [dict.get(target-ele), index]
            dict[ele] = index
    
    """
    普通实现
    """
    def twoSum2(self, nums: List[int], target: int) -> List[int]:
        for index1, ele1 in enumerate(nums):
            for index2, ele2 in enumerate(nums):
                if (index1 != index2) and (ele1 + ele2) == target:
                    # print(ele1 + ele2)
                    return [index1, index2]

if __name__ == "__main__":
    solution = Solution()
    # result = solution.twoSum([2,7,11,15], 9)
    result = solution.twoSum2([2,7,11,15], 9)
    print(result)