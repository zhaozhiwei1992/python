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

class Solution:
    def deleteDuplicates(self, head: ListNode) -> ListNode:
        cur =head
        while cur and cur.next:
            if cur.val==cur.next.val:
                #   找到下一个的情况下，应该继续找不应该去赋值,next.next也可能相等
                cur.next = cur.next.next
                continue
            # else:
            cur=cur.next
        return head

