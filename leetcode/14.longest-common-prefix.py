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
'''
方法1： 太慢
1. 遍历集合(也可以读取字符串位置)当前便利位置后续集合不存在返回空
2. 最早结果存储到一个新得字符串返回

2.换个思路，先排序
不断减少字符串搜索 str.indexof()
'''
class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if(len(strs) < 1):
            return ""
        elif len(strs) == 1:
            return strs[0]
        firstStrSize=len(strs[0])
        returnStr=""
        firstStr = ""
        for i in range(firstStrSize):
            for index, ele in enumerate(strs):
                if(index == 0):
                    firstStr=ele[:i+1]
                else:
                    if index >0 and firstStr != ele[:i+1]:
                        return returnStr
                    elif index == (len(strs)-1):
                        returnStr = firstStr
        return returnStr
if __name__ == "__main__":
    print(Solution().longestCommonPrefix(["flower","flow","flight"]))

