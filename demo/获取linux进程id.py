import os
import sys
import subprocess


def get_process_id(name):
    child = subprocess.Popen(["pgrep", "-f", name], stdout=subprocess.PIPE, shell=False)
    response = child.communicate()[0]
    return response

if __name__ == '__main__':
    pid = get_process_id("while")
    print(pid)
    if not pid:
        print("no target pid to kill,please check")
        sys.exit(1)

    result = os.system("kill -9 " + pid)
    if result == 0:
        print("execute kill success")
    else:
        sys.exit(1)
