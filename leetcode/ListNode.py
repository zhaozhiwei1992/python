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

    def find(self, node, num, a=0):
        while node:
            if a == num:
                return node
            a += 1
            node = node.next

    def add(self, data):
        node = ListNode()
        node.val = data
        node.next = self.cur_node
        self.cur_node = node
        return node

    def printNode(self, node):
        while node:
            print('\nnode: ', node, ' value: ', node.val, ' next: ', node.next)
            node = node.next

    def delete(self, node, num, b=1):
        if num == 0:
            node = node.next
            return node
        while node and node.next:
            if num == b:
                node.next = node.next.next
            b += 1
            node = node.next
        return node

    def reverse(self, nodelist):
        list = []
        while nodelist:
            list.append(nodelist.val)
            nodelist = nodelist.next
        result = ListNode()
        result_handle = Node_handle()
        for i in list:
            result = result_handle.add(i)
        return result
