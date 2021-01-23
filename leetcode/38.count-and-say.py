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
# 题意是n=1时输出字符串1；n=2时，
# 数上次字符串中的数值个数，因为上次字符串有1个1，所以输出11；
# n=3时，由于上次字符是11，有2个1，所以输出21；n=4时，由于上次字符串是21，有1个2和1个1，所以输出1211
#
import re


def strSay(preStr):
    """
    字符串描述
    :param preStr:
    :return:
    """
    result = ""
    # 根据返回值便利，翻译描述, 1, 11, 21, 1211, 111221, 312211
    i = 0
    # // for i in range(len(preStr)), 没法i += 1改变下标
    while i < len(preStr):
        # 统计个数
        count = 1
        # 紧挨着下一个相同数字要统计, 比如上一个1211 --> 111221
        while i + 1 < len(preStr) and preStr[i] == preStr[i + 1]:
            count += 1
            # 统计过的数据要跳过外层遍历
            i += 1
        curStr = str(count) + preStr[i]
        i += 1
        result += curStr
    return result


class Solution:
    def countAndSay(self, n: int) -> str:
        # s = '1'
        # for _ in range(n - 1):
        #     s = re.sub(r'(.)\1*', lambda m: str(len(m.group(0))) + m.group(1), s)
        # return s
        s = '1'
        for _ in range(n - 1):
            s = ''.join(str(len(group)) + digit for group, digit in re.findall(r'((.)\2*)', s))
            # print(s)
        return s

    def countAndSay2(self, n: int) -> str:
        """
        递归处理
        上一次返回结果翻译成语言描述
        :param n:
        :return:
        """
        if n == 0:
            return ""
        if n == 1:
            return "1"

        preStr = self.countAndSay2(n - 1)
        return strSay(preStr)


if __name__ == "__main__":
    print(Solution().countAndSay(9))
    print(Solution().countAndSay2(9))
    # print(strSay("111221"))
