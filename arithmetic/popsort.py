# 冒泡排序: 大数沉底，小数向上, 倒序排列
# 时间复杂度: O(N^2)
# 缺点: 数字越多性能越差
import random

def genRandomList(arrLength):
    # arr=[];
    # for i in range(arrLength):
    #     arr.append(random.randint(0, arrLength))
    return [random.randint(0, arrLength) for i in range(arrLength)]

# 生成一组随机数
arr = genRandomList(int(input("请输入排序数字个数")))
print("排序前数字为: ", arr)

# 冒泡排序相邻比较，每一次都会有一个到头，所以可以减少一次查询范围, 小数冒泡放到最后，倒序
def popSort(arr):
    # n个数只需要n-1趟就可以比较完, 最极端情况比如: 3, 4, 5, 6 比最多只有三个数是小的
    for i in range(1,len(arr)):
        # j 永远从第一位开始, 小的放到后边, 下次遍历就不需要再取管最后一位了,因为每趟肯定确定最小值
        for j in range(len(arr)-i):
            # print("比较过程: 下标:" + str(i) + " -> " + str(arr[j]) + " 和 下标:" +  str(j+1) + " -> " +  str(arr[j+1]))
            if(arr[j] < arr[j+1]):
                mixnum = arr[j] 
                arr[j] = arr[j+1]
                arr[j+1] = mixnum
            print("第 " + str(i) + " 趟结果: " + str(arr))
    return arr;
arr = popSort(arr)
print("排序后结果为: ", arr)

