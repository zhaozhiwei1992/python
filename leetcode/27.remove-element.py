#
# @lc app=leetcode id=27 lang=python3
#
# [27] Remove Element
#
from typing import List
class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        # 方法1   67.88%  5.09%
        # if(len(nums) < 1):
        #     return 0;
        # index = 0
        # while (index < len(nums)):
        #     if (nums[index] == val):
        #         del nums[index]
        #         # 删除后下标改变，还应该在当前位置比较
        #         continue
        #     index = index+1
        # return len(nums)

        # 方法2
        while val in nums:
            nums.remove(val)
