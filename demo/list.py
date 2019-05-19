animal=["cat", "dog", "pig"]
print(animal)
print("pig" in animal)
animal.append("eleph")
animal.sort(reverse=True, key=str.lower)
for i in range(0,len(animal)):
    print(animal[i])

print(animal[0:2])
print(animal[0::-1])
print(animal[-2:-1])
print(animal[::2])
print(tuple(animal))
#  必须完全匹配
s=']'
searchIdex=-1
stack=[]
for s in list(s):
    stackLen = len(stack)
    if(s=="(" or s=="{" or s == "["):
        stack.append(s)
    if(stackLen> 0 and ((s == "]" and stack[stackLen-1] == "[") or (s == ")" and stack[stackLen-1] == "(") or (s == "}" and stack[stackLen-1] == "{") )):
        stack.pop()
print(stack)

nums=[1,1,2,3]
print(len(set(nums)))

# 牛逼的语法啊, for前面的num可以做其他操作然后构成集合
nums = [num for num in range(6)]
print (nums)
