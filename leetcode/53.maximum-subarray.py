#
# @lc app=leetcode id=53 lang=python3
#
# cursum: -2 x: 1 maxsum: -2\n
# cursum: 1 x: -3 maxsum: 1\n
# cursum: -2 x: 4 maxsum: 1\n
# cursum: 4 x: -1 maxsum: 4\n
# cursum: 3 x: 2 maxsum: 4\n
# cursum: 5 x: 1 maxsum: 5\n
# cursum: 6 x: -5 maxsum: 6\n
# cursum: 1 x: 4 maxsum: 6
# [53] Maximum Subarray
#

from typing import List


class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        if not nums:
            return 0
        cursum = maxsum = nums[0]
        #  求所有数和最大, 每次尽量最大, 当前的最大不一定最大，还要与上一次的比较
        for x in nums[1:]:
            # print("cursum: " + str(cursum) + " x: " + str(x) + " maxsum: " + str(maxsum))
            cursum = max(x, x + cursum)
            maxsum = max(maxsum, cursum)
        return maxsum


if __name__ == '__main__':
    print(Solution().maxSubArray([1, 2, 3, 9, 6]))
