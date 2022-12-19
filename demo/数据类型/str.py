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

# 格式： [start:end:step]
#
# • [:] 提取从开头（默认位置0）到结尾（默认位置-1）的整个字符串
# • [start:] 从start 提取到结尾
# • [:end] 从开头提取到end - 1
# • [start:end] 从start 提取到end - 1
# • [start:end:step] 从start 提取到end - 1，每step 个字符提取一个
# • 左侧第一个字符的位置/偏移量为0，右侧最后一个字符的位置/偏移量为-1
slice_str = '12345'
print("从0开始3个字符", slice_str[0:3:])
print("从头到尾", slice_str[:])
print("最后一个字符", slice_str[-1:])
