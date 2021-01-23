#
# @lc app=leetcode id=83 lang=python3
#
# [83] Remove Duplicates from Sorted List
#
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

from ListNode import *

class Solution:
    def deleteDuplicates(self, head: ListNode) -> ListNode:
        """
        只能删除相邻节点
        :param head:
        :return:
        """
        cur = head
        while cur and cur.next:
            if cur.val == cur.next.val:
                #   找到下一个的情况下，应该继续找不应该去赋值,next.next也可能相等
                cur.next = cur.next.next
                continue
            # else:
            cur = cur.next
        return head


if __name__ == '__main__':

    l1 = ListNode()
    ListNode_1 = Node_handle()
    l1_list = [1, 1, 2]
    for i in l1_list:
        l1 = ListNode_1.add(i)
    sol = Solution()
    Node_handle().printNode(sol.deleteDuplicates(l1))
