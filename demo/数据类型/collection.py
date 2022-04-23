def twoSum(nums, target):
    # for index1, ele1 in enumerate(nums):
    #     for index2, ele2 in enumerate(nums):
    #         if index1 != index2 and (ele1 + ele2) == target:
    #             print(ele1 + ele2)
    #             return [index1, index2]
    dict = {}
    for index, ele in enumerate(nums):
        if dict.keys().__contains__(target - ele):
            return [dict.get(target-ele), index]
        dict[ele] = index

if __name__ == "__main__":
    print(twoSum([3,2,4], 6))
