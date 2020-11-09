#
# @lc app=leetcode id=21 lang=python3
#
# [21] Merge Two Sorted Lists
#
# Definition for singly-linked list.

class ListNode:
    def __init__(self):
        self.val = None
        self.next = None

"""
node 创建并增加元素
"""
class Node_handle():
    def __init__(self):
        self.cur_node = None
    def find(self,node,num,a = 0):
        while node:
            if a == num:
                return node
            a += 1
            node = node.next
    def add(self,data):
        node = ListNode()
        node.val = data
        node.next = self.cur_node
        self.cur_node = node
        return node
    def printNode(self,node):
        while node:
            print ('\nnode: ', node, ' value: ', node.val, ' next: ', node.next)
            node = node.next
    def delete(self,node,num,b = 1):
        if num == 0:
            node = node.next
            return node
        while node and node.next:
            if num == b:
                node.next = node.next.next
            b += 1
            node = node.next
        return node
    def reverse(self,nodelist):
        list = []
        while nodelist:
            list.append(nodelist.val)
            nodelist = nodelist.next
        result = ListNode()
        result_handle =Node_handle()
        for i in list:
            result = result_handle.add(i)
        return result

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
        if(l1.val > l2.val):
            result = l2
            result.next=self.mergeTwoListsRecu(l1, l2.next)
        else:
            result = l1
            result.next=self.mergeTwoListsRecu(l1.next, l2)
        return result


if __name__ == "__main__":
    l1 = ListNode()
    ListNode_1 = Node_handle()
    l1_list = [1, 2, 3]
    for i in l1_list:
        l1 = ListNode_1.add(i)

    l2 = ListNode()
    ListNode_2 = Node_handle()
    l2_list = [3,2, 4]
    for i in l2_list:
        l2 = ListNode_2.add(i)

    sol = Solution()
    # Node_handle().printNode(sol.mergeTwoLists(l1, l2))
    Node_handle().printNode(sol.mergeTwoListsRecu(l1, l2))
