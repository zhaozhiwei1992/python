#!/usr/bin/env python3
import sys
from collections import Counter
class Person(object):

    def __init__(self, name):
        self.name = name

    def get_details(self):
        return self.name

    def get_grade(self):
        pass

class Student(Person):

    def get_grade(self):
        c = Counter(self.grades)
        passes = c['A'] + c['B'] + c['C']
        fails = c['D']
        return 'Pass: ' + str(passes) + ', Fail: ' + str(fails)

    def __init__(self, name, branch, year, grades):
        Person.__init__(self, name)
        self.branch = branch
        self.year = year
        self.grades = grades

    def get_details(self):
        return "{} studies {} and is in {} year.".format(self.name, self.branch, self.year)


class Teacher(Person):

    def get_grade(self):
        c = Counter(self.grades).most_common(4)
        for x, y in c:
            self.var += (x + ': ' +  str(y) + ', ')
        return self.var

    def __init__(self, name, papers, grades):
        Person.__init__(self, name)
        self.papers = papers
        self.grades = grades
        self.var = ''

    def get_details(self):
        return "{} teaches {}".format(self.name, ','.join(self.papers))

if __name__ == '__main__':

    value = sys.argv[1]
    if(value == 'teacher'):
        person = Teacher('zhangsan', ['c', 'java'], sys.argv[2])
        print(person.get_grade())
    elif(value == 'student'):
        person = Student('Kushal', 'CSE', 2005, sys.argv[2])
        print(person.get_grade())

