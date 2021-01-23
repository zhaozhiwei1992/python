#
# @lc app=leetcode id=14 lang=python3
#
# [14] Longest Common Prefix
#
# https://leetcode.com/problems/longest-common-prefix/description/
#
# algorithms
# Easy (33.18%)
# Total Accepted:    431.8K
# Total Submissions: 1.3M
# Testcase Example:  '["flower","flow","flight"]'
#
# Write a function to find the longest common prefix string amongst an array of
# strings.
# 
# If there is no common prefix, return an empty string "".
# 
# Example 1:
# 
# 
# Input: ["flower","flow","flight"]
# Output: "fl"
# 
# 
# Example 2:
# 
# 
# Input: ["dog","racecar","car"]
# Output: ""
# Explanation: There is no common prefix among the input strings.
# 
# 
# Note:
# 
# All given inputs are in lowercase letters a-z.
# 
#
from typing import List

'''
方法1： 太慢
1. 遍历集合(也可以读取字符串位置)当前便利位置后续集合不存在返回空
2. 最早结果存储到一个新得字符串返回

2.换个思路，先排序
不断减少字符串搜索 str.indexof()
'''


class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if len(strs) < 1:
            return ""
        elif len(strs) == 1:
            return strs[0]
            # 第一个字符串长度，获取公共，这里用哪个都可以, 理论上用最短的更好
        # firstStrSize=len(strs[0])
        minStrSize = len(min(strs, key=len))
        returnStr = ""
        firstStr = ""
        #  根据最短字符串长度，每个字符串获取进行匹配
        for i in range(minStrSize):
            for index, ele in enumerate(strs):
                # 获取第一个字符串的字符
                if (index == 0):
                    firstStr = ele[:i + 1]
                else:
                    if index > 0 and firstStr != ele[:i + 1]:
                        # 有一步匹配不了就返回现有的匹配结果
                        return returnStr
                    elif index == (len(strs) - 1):
                        # 一轮全部便利完成，到了这里说明第一轮匹配成功
                        returnStr = firstStr
        return returnStr


if __name__ == "__main__":
    print(Solution().longestCommonPrefix(["flower", "flow", "flight"]))
