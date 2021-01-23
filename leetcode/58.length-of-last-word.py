#
# @lc app=leetcode id=58 lang=python3
#
# [58] Length of Last Word
#
import re


class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        """
        最后一个单词长度，　空格分隔
        :param s:
        :return:
        """
        result = re.findall(r'[A-Za-z][^ ]*', s)
        length = len(result)
        if length == 0:
            return 0
        else:
            # return the length of last word in the string.
            return len(result[length - 1])


if __name__ == '__main__':
    print(Solution().lengthOfLastWord("helloworld"))
