nums = [2, 4, 6, 8, 9]
#  所有大于２的数字乘以２后放入集合中
nums = [i * 2 for i in nums if i > 2]
print(nums)

animal = ["cat", "dog", "pig"]
#  全部输出
print(animal)
#  true
print("pig" in animal)
animal.append("eleph")
# 反向输出
animal.sort(reverse=True, key=str.lower)
print('倒序输出animal -- begin')
for i in range(0, len(animal)):
    print(animal[i])
print('倒序输出animal -- end')

# 切片包括前数不包括后数
print('0::2', animal[0:2])
print('0::-1', animal[0::-1])
print('0:-1', animal[0:-1])
print('-2::-1', animal[-2:-1])
print('::2', animal[::2])
print('tuple', tuple(animal))

#  必须完全匹配
s = ']'
searchIdex = -1
stack = []
for s in list(s):
    stackLen = len(stack)
    if s == "(" or s == "{" or s == "[":
        stack.append(s)
    if (stackLen > 0 and ((s == "]" and stack[stackLen - 1] == "[") or (s == ")" and stack[stackLen - 1] == "(") or (
            s == "}" and stack[stackLen - 1] == "{"))):
        stack.pop()
print(stack)

nums = [1, 1, 2, 3]
print(len(set(nums)))

# 牛逼的语法啊, for前面的num可以做其他操作然后构成集合
nums = [num for num in range(6)]
print(nums)
