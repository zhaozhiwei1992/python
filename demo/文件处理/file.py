import os

# 当前工作目录
print(os.getcwd())
# 更改工作目录
# os.chdir("xx")

print(os.path.abspath(os.path.join("/d", 'blog', 'x.md')))

# 创建文件夹 os.mkkedirs (会创建根目录及子目录)
if not os.path.exists("D:\\tmp\\pythontest\\1"):
    os.makedirs("D:\\tmp\\pythontest\\1")

# 判断是否绝对路径是根据路径字符串格式来进行，而不是这个路径是否真实存在
print(os.path.abspath(".."))
print(os.path.isabs(os.path.abspath("..")))
print(os.path.isabs("/xx"))

# 相对路径: 字符串比较， 路径不一定真实存在
print(os.path.relpath("C:\\windows", "c:\\"))

path = "D:\\workspace\\python\\demo"
# 获取路径中的文件部分
print(os.path.basename(path))
# 获取路径中的文件夹路径
print(os.path.dirname(path))
# 获取路径元组， 包含路径部分和文件部分
print(os.path.split(path))
# 路径中每个部分都拆分到list中
print(path.split(os.path.sep))

# 查看文件大小和文件夹内容
# 文件字节数
print(os.path.getsize(path))
# 文件列表
print(os.listdir(path))
# 统计 当前目录 下文件大小
totalSize = 0
for filename in os.listdir(path):
    totalSize += os.path.getsize(os.getcwd() + "\\" + filename)
print(totalSize)

# 文件是否存在
print(os.path.exists("D:\\tmp\\pythontest\\1"))
print(os.path.isdir("D:\\tmp\\pythontest\\1\\22.txt"))

# 读写文件
helloFile = open("D:\\tmp\\pythontest\\1\\hello.txt")

# read 和readlines不能同时存在
# print("文件读取内容:\n" + helloFile.read())
print("读取文件内容列表:\n")
print(helloFile.readlines())
helloFile.close()

helloFile = open("D:\\tmp\\pythontest\\1\\hello.txt", "a")
helloFile.write("wocao")
helloFile.close()

# shelve 模块保存变量 (类似java序列化??)
