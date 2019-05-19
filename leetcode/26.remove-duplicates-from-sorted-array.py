#
# @lc app=leetcode id=26 lang=python3
# Do not allocate extra space for another array, you must do this by modifying the input array in-place with O(1) extra memory.
#
# [26] Remove Duplicates from Sorted Array
#
class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        # 这个方式不行，要求不能重新创建list并且要改变原有的
        # 如果原来是[1,1,2], 那么最后前俩位必须是1,2
        # return len(list(set(nums)))

        # 方法1： 速度太慢，超过33%
        # if len(nums) == 0:
        #     return 0
        # elif (len(nums) == 1):
        #     return 1
        # elif len(set(nums)) == 1:
        #     n=1
        #     while(n < len(nums)):
        #         del nums[n]
        #         n=n+1
        #     return 1
        # else:
        #     n = 0
        #     while(n < len(nums)):
        #         if(nums[n]==nums[n-1]):del nums[n]
        #         else:n += 1
        #     return n

        # 参考leetcode大佬的写法，速度快 88+%
        if not nums:
            return 0
        else:
            ii,jj=1,1
            while jj<len(nums):
                print(ii, '---', jj)
                if nums[ii-1]!=nums[jj]:
                    nums[ii]=nums[jj]
                    ii+=1
                jj+=1
            return ii
