# Python中json是一个非常常用的模块，这个主要有4个方法：
#
#     json.dumps
#     json.dump
#     json.loads
#     json.load
# 不相同点：
#
#     loads操作的是字符串
#     load操作的是文件流
#
# 1.2 相同点
#
#     除了第一个参数（要转换的对象）类型不同，其他所有的参数都相同
#     最终都是转换成Python对象

import json

s = '{"name": "wade", "age": 54, "gender": "man"}'
# json.loads读取字符串并转为Python对象
print("json.loads将字符串转为Python对象: type(json.loads(s)) = {}".format(type(json.loads(s))))
print("json.loads将字符串转为Python对象: json.loads(s) = {}".format(json.loads(s)))

# json.load读取文件并将文件内容转为Python对象
# 数据文件要s.json的内容 --> {"name": "wade", "age": 54, "gender": "man"}
with open('s.json', 'r') as f:
    s1 = json.load(f)
    print("json.load将文件内容转为Python对象: type(json.load(f)) = {}".format(type(s1)))
    print("json.load将文件内容转为Python对象: json.load(f) = {}".format(s1))