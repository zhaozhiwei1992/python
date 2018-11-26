# 捅排序, 空间换时间
# 缺点：每次搞出来很多捅，而且被排序的数最大值越大，捅就越多, 例如: 我就排三个数字 都是超过一个亿的，那就得造1亿以上的捅 
# 要求: 给定一些数字， 使用O(M+N) 方式进行排序
import random
# 传入要生成的数字个数
# print("请输入要排序数字个数:")
n = int(input("请输入要排序数字个数:"))
# 使用程序随机生成，并输入排序前数
arr=[];
for i in range(0, n):
    arr.append(random.randint(0, n-1)) # 这里使用n-1是为了不超过捅的下标，例如，列表中有10，但是捅只到了a[9]
print("排序前数字为: ", arr)
# 捅排序算法
def bucketsort(arr):
    # 创建小桶, 初始化为0, 小桶的编号为当前排序数字, 最终桶里放的是出现次数
    buckets=[0]*n

    # print(buckets)
    # print(arr)
    # 每个数字出现一次就+1
    for i in arr:
        buckets[i] += 1

    result=[];
    # print(buckets[::-1])
    # 正序排列, enumerate这个方法可以同时返回下标和要素
    # for i, var in enumerate(buckets):
    #     # print("当前个数" + str(var) + "当前位置: " + str(i))
    #     for j in range(var):
    #         result.append(i)
    #倒序排列, [::-1]表示倒序
    for i in range(len(buckets))[::-1]:
        for j in range((buckets[i])):
            result.append(i)
    return result
result=bucketsort(arr)
# 输出排序结果
print("排序后结果为: ", result)
