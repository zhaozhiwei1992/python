#
# @lc app=leetcode id=21 lang=python3
#
# [21] Merge Two Sorted Lists
#
# Definition for singly-linked list.

from ListNode import *


class Solution:
    def mergeTwoLists(self, l1: ListNode, l2: ListNode) -> ListNode:
        # head和cur里最终放完整listnode关系
        result = cur = ListNode()
        # l1 l2 Node全部存在
        while l1 and l2:
            # 值比较小的先放到里边
            if l1.val > l2.val:
                cur.next = l2
                l2 = l2.next
            else:
                cur.next = l1
                l1 = l1.next
            cur = cur.next
        cur.next = l1 or l2
        return result.next

    def mergeTwoListsRecu(self, l1: ListNode, l2: ListNode) -> ListNode:
        if not l1:
            return l2
        elif not l2:
            return l1

        # result指向更小的节点
        if (l1.val > l2.val):
            result = l2
            result.next = self.mergeTwoListsRecu(l1, l2.next)
        else:
            result = l1
            result.next = self.mergeTwoListsRecu(l1.next, l2)
        return result


if __name__ == "__main__":
    l1 = ListNode()
    ListNode_1 = Node_handle()
    l1_list = [1, 2, 3]
    for i in l1_list:
        l1 = ListNode_1.add(i)

    l2 = ListNode()
    ListNode_2 = Node_handle()
    l2_list = [3, 2, 4]
    for i in l2_list:
        l2 = ListNode_2.add(i)

    sol = Solution()
    # Node_handle().printNode(sol.mergeTwoLists(l1, l2))
    Node_handle().printNode(sol.mergeTwoListsRecu(l1, l2))
