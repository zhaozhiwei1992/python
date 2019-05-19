strs=["aa","a"]
strs.sort(key=lambda x:len(x))
# print(strs)
yourlen = len(strs[0]);
for i in range(yourlen):
    for ele in strs:
        if str(ele).index(strs[0][:yourlen-i]) > -1:
            print(strs[0][:yourlen-i])
# firstStrSize=len(strs[0])
# returnStr=""
# firstStr = ""
# for i in range(firstStrSize):
#     for index, ele in enumerate(strs):
#         if(index == 0):
#             firstStr=ele[:i+1]
#         else:
#             if index >0 and firstStr != ele[:i+1]:
#                 # return returnStr
#                 break
#             elif index == (len(strs)-1):
#                 returnStr = firstStr
# print(returnStr)
# class Solution:
#     def reverse(self, x: int) -> int:
#         maxint = 2<<30
#         minint = -2<<30
#         if(x > maxint or (x <= minint)):
#             return 0
#         # 反转
#         s = str(abs(x)) 
#         # int化
#         i = int(s[::-1]) 
#         if(x > 0 and i <= maxint):
#             return i
#         elif(x < 0 and (0-i) >= minint):
#             return 0-i
#         else:
#             return 0
# if __name__ == "__main__":
#     print(Solution().reverse(-2147483648))