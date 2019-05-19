# 这题真没想到， copy的代码
# @lc app=leetcode id=38 lang=python3
#
# [38] Count and Say
# 1.     1
# 2.     11
# 3.     21
# 4.     1211
# 5.     111221
# 1 is read off as "one 1" or 11.
# 11 is read off as "two 1s" or 21.
# 21 is read off as "one 2, then one 1" or 1211.
#
class Solution:
    def countAndSay(self, n: int) -> str:
        # s = '1'
        # for _ in range(n - 1):
        #     s = re.sub(r'(.)\1*', lambda m: str(len(m.group(0))) + m.group(1), s)
        # return s
        s = '1'
        for _ in range(n - 1):
            s = ''.join(str(len(group)) + digit for group, digit in re.findall(r'((.)\2*)', s))
            print(s)
        return s 

