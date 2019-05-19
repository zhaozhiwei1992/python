import re
# 1.     1
# 2.     11
# 3.     21
# 4.     1211
# 5.     111221
# 1 is read off as "one 1" or 11.
# 11 is read off as "two 1s" or 21.
# 21 is read off as "one 2, then one 1" or 1211.

# >>> re.findall(r'((.)\2*)', '1211')
#  [('1', '1'), ('2', '2'), ('11', '1')]   # 前边为group后边为digit 因为有俩个分组

# 循环输出
# group长度: 1
# 1
# 11
# group长度: 1
# 2
# 12
# group长度: 2
# 1
# 21

n=2
s = '1211'
for _ in range(n - 1):
    # print(_)
    for group, digit in re.findall(r'((.)\2*)', s):
        print("group长度: " + str(len(group)))
        print(digit)
        print(str(len(group)) + digit)
    # s = ''.join(str(len(group)) + digit for group, digit in re.findall(r'((.)\2*)', s))
    # print(s)
