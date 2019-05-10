#
# @lc app=leetcode id=58 lang=python3
#
# [58] Length of Last Word
#
class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        result = re.findall(r'[A-Za-z][^ ]*', s)
        length = len(result)
        if length == 0: return 0
        else:
            # return the length of last word in the string.
            return len(result[length-1])

