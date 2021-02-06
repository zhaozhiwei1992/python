#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import argparse
import getopt
import sys


def sysFunc():
    """
    基于 sys 模块的简单参数解析功能
    选项的写法要求:
  　　对于短格式:
          "-"号后面要紧跟一个选项字母，如果还有此选项的附加参数，可以用空格分开，也可以不分开。
          长度任意，可以用引号。
          如： -h  -ls -l s  等等
    对于长格式：
         "--"号后面要跟一个单词，如果还有些选项的附加参数，后面要紧跟"="，再加上参数。
         "="号前后不能有空格。
         如： --input=data.txt
    长格式是在Linux下引入的，许多Linux程序都支持这两种格式。在Python中提供了getopt模块很好
    的实现了对着两种用法的支持，而且使用简单。
    执行示例：
         python use_params.py -d data.txt
         python use_params.py --data=data.txt
    """

    if len(sys.argv) == 1:
        print('Nothing need to be done!')
        sys.exit()
    else:
        para_list = sys.argv
        print('Parameters is: ', para_list)
        if para_list[1].startswith('--'):
            print('DataFile name is: ', para_list[1].split('=')[-1].strip())
            print('Longopts,do your actions here!!!')
        elif para_list[1].startswith('-'):
            print('DataFile name is: ', para_list[2])
            print('Shortopts,do your actions here!!!')


def getOptFunc():
    """
     python use_params.py -i 172.19.7.217 -p 8066 data.txt 88
      python use_params.py --ip=172.19.7.217 --port=8066 data.txt 88
    """
    if len(sys.argv) == 1:
        print
        'Nothing need to be done!'
        sys.exit()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:i:", ["help", "ip=", "port="])  # 过滤掉脚本名称
        '''
        opts是个包含元祖的列表,args是个列表，包含那些没有‘-'或‘--'的参数
        短格式 --- h 后面没有冒号：表示后面不带参数，p：和 i：后面有冒号表示后面需要参数
        长格式 --- help后面没有等号=，表示后面不带参数，其他三个有=，表示后面需要参数
        '''
        print('opts: ', opts)
        print('args: ', args)
    except getopt.GetoptError:
        print("argv error,please input")
        sys.exit()
        # 打印具体参数
    map_dict = {'-i': 'IP', '--ip': 'IP', '-p': 'Port', '--port': 'Port'}
    for name, value in opts:
        if name in ("-h", "--help"):
            print("""
             Usage:sys.args[0] [option]
             -h or --help：显示帮助信息
             -p or --ip： IP地址
             -p or --port： IP端口
             """)
        if name in ('-i', '--ip', '-p', '--port'):
            print('{0} is=======>{1}'.format(map_dict[name], value))


def argparseFunc():
    """
    基于argparse模块实现高级的参数解析功能
    default 默认值
    执行示例：
         python use_params.py -i 172.19.7.236 -p 7077 -f -w
         python use_params.py -i 172.19.7.236 -p 7077 -f -r

         python user_params.py -h
         show example

optional arguments:
  -h, --help            show this help message and exit
  -i IP, --ip IP        IP Address
  -p PORT, --port PORT  IP Port
  -f, --flag            Flag
  -r, --read            Read Action
  -w, --write           Write Action

    """
    parser = argparse.ArgumentParser(description="show example")  # 使用argparse的构造函数来创建对象
    parser.add_argument("-i", "--ip", default="127.0.0.1", help="IP Address")  # 添加可解析的参数
    parser.add_argument("-p", "--port", help="IP Port")  # 添加可解析的参数
    parser.add_argument("-f", "--flag", help="Flag", action="store_true")  # action=store_true的意义是如果使用了这个参数则值默认为TRUE
    exptypegroup = parser.add_mutually_exclusive_group()  # 添加一组互斥的选项，如上例中的-l和-r只能用一个
    exptypegroup.add_argument("-r", "--read", help="Read Action", action="store_true")
    exptypegroup.add_argument("-w", "--write", help="Write Action", action="store_true")
    ARGS = parser.parse_args()
    print('ARGS:', ARGS)
    if ARGS.ip:
        print("IP is: " + ARGS.ip)
    if ARGS.port:
        print("Port is: " + ARGS.port)
    if ARGS.flag:
        print("Flag is: " + str(ARGS.flag))
    if ARGS.read:
        print("Read action is: " + str(ARGS.read))
    if ARGS.write:
        print("Write action is: " + str(ARGS.write))


if __name__ == '__main__':
    # sysFunc()
    # getOptFunc()
    argparseFunc()
