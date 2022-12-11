import os
import time

def isLocked():
    result = os.system("fuser /var/lock/slim.lock")
    if result == 0:
        print("execute kill success")
        print("11xxx", result)
        return False
    else:
        print("222", result)
        return True


if __name__ == '__main__':
    while True:
        time.sleep(5)
        isLocked()
