#
# @lc app=leetcode id=21 lang=python3
#
# [21] Merge Two Sorted Lists
#
# Definition for singly-linked list.
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

def list_2_ListNode(array):
    tem_node = ListNode(0)
    node = ListNode(0)
    for i  in array:
        #记得是判定val是否有值，并且用一个node记住头节点，然后返回的是头节点          
        if not tem_node.val:
            tem_node.val =i
            node = tem_node
        else:
            tem_node.next = ListNode(i)
            tem_node = tem_node.next
    return node

class Solution:
    def mergeTwoLists(self, l1, l2):
        head = cur = ListNode(0)
        while l1 and l2:
            if l1.val > l2.val:
                cur.next = l2
                l2 = l2.next
            else:
                cur.next = l1
                l1 = l1.next
            cur = cur.next
        cur.next = l1 or l2
        return head.next

if __name__ == "__main__":
    arr1 = [1,3,2]
    nodes = list_2_ListNode(arr1)
    # print(nodes.next.val)
    # print("hh")
    # sol = Solution()
    # print(sol.mergeTwoLists(list_2_ListNode([1,2,3]), list_2_ListNode([3,2,4])))