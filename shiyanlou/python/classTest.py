#!/usr/bin/env python3

class Person(object):
    """
    返回具有给定名称的 Person 对象
    """

    def __init__(self, name):
        self.name = name

    def get_details(self):
        """
        返回包含人名的字符串
        """
        return self.name


class Student(Person):
    """
    返回 Student 对象，采用 name, branch, year 3 个参数
    """

    def __init__(self, name, branch, year):
        Person.__init__(self, name)
        self.branch = branch
        self.year = year

    def get_details(self):
        """
             返回包含学生具体信息的字符串
             """
        return "{} studies {} and is in {} year.".format(self.name, self.branch, self.year)


class Teacher(Person):
    """
    返回 Teacher 对象，采用字符串列表作为参数
    """

    def __init__(self, name, papers):
        Person.__init__(self, name)
        self.papers = papers

    def get_details(self):
        return "{} teaches {}".format(self.name, ','.join(self.papers))


class Account(object):
    """账号类,
    amount 是美元金额.
    """
    def __init__(self, rate):
        self.__amt = 0
        self.rate = rate

    @property
    def amount(self):
        """账号余额（美元）"""
        return self.__amt

    @property
    def cny(self):
        """账号余额（人名币）"""
        return self.__amt * self.rate

    @amount.setter
    def amount(self, value):
        if value < 0:
            print("Sorry, no negative amount in the account.")
            return
        self.__amt = value

import os
def view_dir(path='.'):
    """
    这个函数打印给定目录中的所有文件和目录
    :args path: 指定目录，默认为当前目录
    """
    names = os.listdir(path)
    names.sort()
    for name in names:
        print(name, end =' ')
    print()


if __name__ == '__main__':
    view_dir('/')
    # acc = Account(rate=6.6)  # 基于课程编写时的汇率
    # acc.amount = 20
    # print("Dollar amount:", acc.amount)
    # print("In CNY:", acc.cny)
    # acc.amount = -100
    # print("Dollar amount:", acc.amount)

    # person1 = Person('Sachin')
    # student1 = Student('Kushal', 'CSE', 2005)
    # teacher1 = Teacher('Prashad', ['C', 'C++'])
    #
    # print(person1.get_details())
    # print(student1.get_details())
    # print(teacher1.get_details())

    # parent index suns obj
    # person = Person('Sachin')
    # print(person.get_details())
    # person = Student('Kushal', 'CSE', 2005)
    # print(person.get_details())
    # person = Teacher('Prashad', ['C', 'C++'])
    # print(person.get_details())
