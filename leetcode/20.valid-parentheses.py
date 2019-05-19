#
# @lc app=leetcode id=20 lang=python3
#
# [20] Valid Parentheses
#
# https://leetcode.com/problems/valid-parentheses/description/
#
# algorithms
# Easy (36.13%)
# Total Accepted:    548.2K
# Total Submissions: 1.5M
# Testcase Example:  '"()"'
#
# Given a string containing just the characters '(', ')', '{', '}', '[' and
# ']', determine if the input string is valid.
# 
# An input string is valid if:
# 
# 
# Open brackets must be closed by the same type of brackets.
# Open brackets must be closed in the correct order.
# 
# 
# Note that an empty string is also considered valid.
# 
# Example 1:
# 
# 
# Input: "()"
# Output: true
# 
# 
# Example 2:
# 
# 
# Input: "()[]{}"
# Output: true
# 
# 
# Example 3:
# 
# 
# Input: "(]"
# Output: false
# 
# 
# Example 4:
# 
# 
# Input: "([)]"
# Output: false
# 
# 
# Example 5:
# 
# 
# Input: "{[]}"
# Output: true
# 
# 
#
import re
class Solution:
    def isValid(self, s: str) -> bool:
        #  必须完全匹配
        searchIdex=-1
        stack=[]
        for s in list(s):
            stackLen = len(stack)
            if(s=="(" or s=="{" or s == "["):
                stack.append(s)
            elif(stackLen> 0 and ((s == "]" and stack[stackLen-1] == "[") or (s == ")" and stack[stackLen-1] == "(") or (s == "}" and stack[stackLen-1] == "{") )):
                stack.pop()
            else:
                return False
        return len(stack) == 0
