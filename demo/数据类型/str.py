print("{} {}".format("hello", "world"))
# tuple作为参数不能用format传，否则会出现index溢出
print("%s %s" % ("hello", "world"))
print(
    "insert into standard_field (table_name, code, name, type, length, required) values ('{}', '{}', '{}', '{}', '{}', '{}')".format(
        'ELE_CATALOG', 'ELE_CATALOG_ID', '目录主键', 'String', '38', '1'))

str = "|"
joinstr = str.join(["pig", "dog", "cat"])
print(joinstr)

print("hello".rjust(20, "*"))

# 自然字符串,转移之类的全部不作处理
print(r"hello\nxxx\rnima")

print("hh\n 换行了")

# 带有非英文字符时，有时候需要使用unicode
print(u"This is a Unicode string.\n 这是带有中文的字符串")

# 相邻字符串自动连接, 不用使用+号
print('hh ' '\n' 'hello')

# 多个物理行一个逻辑行, 最后加换行符
# 结果: hello my name is     hhhhhhhh
print('hello my name is \
    hhhhhhhh')

name = 'Swaroop'  # This is a string object
if name.startswith('Swa'):
    print('Yes, the string starts with "Swa"')

if 'a' in name:
    print('Yes, it contains the string "a"')

if name.find('war') != -1:
    print('Yes, it contains the string "war"')

delimiter = '_*_'
mylist = ['Brazil', 'Russia', 'India', 'China']
print(delimiter.join(mylist))

print("测试字符串切片", "12345"[0:3:])
