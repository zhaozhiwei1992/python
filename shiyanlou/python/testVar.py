#!/usr/bin/env python3
# def change():
#     global a
#     a = 90
#     print(a)
# a = 9
# print("Before the function call ", a)
# print("inside change function", end=' ')
# change()
# print("After the function call ", a)

def test(a, b= -90):
    if a > b:
        return True;
    else:
        return False

if __name__ == '__main__':
    print(test(1)) # True
    print(test(1, 0)) # True
    print(test(1, 2)) # False