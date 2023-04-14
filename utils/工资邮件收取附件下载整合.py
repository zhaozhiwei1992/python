# !user/bin/python
# _*_ coding: gb2312 _*_
#
# @Title: 工资邮件收取附件下载整合.py
# @Description: 下载工资明细并整合到一个统一的excel或者org中
# @author zhaozhiwei
# @date 2023/4/13 上午10:43
# @version V1.0

import email
import os
import poplib
import zipfile
from email.header import decode_header
from email.parser import Parser
from email.utils import parseaddr

# 读取excel
import openpyxl
import rarfile


def decode_str(s):
    """
    # 字符编码转换
    """
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def get_att(msg, savepath):
    """
    下载附件
    savepath: 直接写好文件名
    """
    attachment_files = []
    for part in msg.walk():
        file_name = part.get_filename()  # 获取附件名称类型
        contType = part.get_content_type()
        if file_name:
            h = email.header.Header(file_name)
            # 对附件名称进行解码
            dh = email.header.decode_header(h)
            filename = dh[0][0]
            if dh[0][1]:
                filename = decode_str(str(filename, dh[0][1]))  # 将附件名称可读化
                print("邮件中附件名称", filename)
                # filename = filename.encode("utf-8")
            data = part.get_payload(decode=True)  # 下载附件
            # 在指定目录下创建文件，注意二进制文件需要用wb模式打开
            # 这里附件名字用subject名, 方便区分
            # att_file = open(savepath + "\\/" + filename, 'wb')
            att_file = open(savepath, 'wb')
            attachment_files.append(savepath)
            att_file.write(data)  # 保存附件
            att_file.close()
    return attachment_files


def dcompress(savepath):
    """
    获取所有的 名字里带工资条的rar文件
    """
    # 工资条rar解压缩密码
    dcompressPassWord = os.environ['PAY_STUPS_PASSWORD']
    for root, dirs, files in os.walk(savepath):
        try:
            for file in files:
                if "工资条" not in file:
                    continue
                if ".zip" in os.path.splitext(file)[1]:
                    path = os.path.join(savepath, file)
                    os.chdir(savepath)
                    zip = zipfile.ZipFile(file)  # 待解压文件
                    # zip.extractall(src_dir1) # 解压指定文件
                    zip.extractall(savepath)
                    zip.close()
                    os.remove(path)
                if ".rar" in os.path.splitext(file)[1]:
                    path = os.path.join(savepath, file)
                    # os.chdir(savepath)
                    rf = rarfile.RarFile(path)
                    # 内部文件名相同, 所以解压到同名文件夹
                    dcompress_path = os.path.join(savepath, os.path.splitext(file)[0])
                    rf.extractall(path=dcompress_path, pwd=dcompressPassWord)
                    # 解压指定路径
                    rf.close()
                    # 解压后删除文件
                    # os.remove(path)
        except Exception as err:
            print(err)


def connect_mail():
    """
    连接邮箱
    """
    # 连接到POP3服务器
    # # POP3服务器、用户名、密码
    # 此处密码是授权码,用于登录第三方邮件客户端
    password = os.environ['MAIL_126_PASSWORD']
    username = os.environ['MAIL_126_USERNAME']
    host = 'pop3.126.com'
    server = poplib.POP3(host)
    server.user(username)
    # 参数是你的邮箱密码，如果出现poplib.error_proto: b'-ERR login fail'，就用开启POP3服务时拿到的授权码
    server.pass_(password)
    # stat()返回邮件数量和占用空间:
    print('Messages: %s. Size: %s' % server.stat())
    return server


def excel_archive(savepath):
    """
    处理工资excel, 解析数据, 合并生成csv格式数据
    """
    dataList = []
    for root, dirs, files in os.walk(savepath):
        try:
            for dir in dirs:
                # 读取带有 工资条 的文件夹, 读取里边的xlsx文件
                if "工资条" not in dir:
                    continue
                # 获取每个目录下文件 LT-1336_赵志伟.xlsx
                file_name = os.path.join(root, dir, 'LT-1336_赵志伟.xlsx')
                wb = openpyxl.load_workbook(file_name)
                sheet = wb.worksheets[0]
                # 不同年度单元格位置不同, 需要单独处理
                # 一般都是放在第4行
                # dir: xx年x月工资条
                item = {}
                item['时间'] = str(dir).replace("工资条", "").replace("年", "-").replace("月", "")
                year = str(item['时间']).split('-')[0]
                month = str(item['时间']).split('-')[1]
                # 根据不同年度文件格式不同，分别处理, 因只有一条数据, 转换成map即可
                if year in ['2017', '2018']:
                    item['实发'] = sheet['G' + str(4)].value
                    item['个税'] = sheet['Y' + str(4)].value
                    item['养老'] = sheet['R' + str(4)].value
                    item['医疗'] = sheet['S' + str(4)].value
                    item['公积金'] = sheet['U' + str(4)].value
                    if year == '2018' and month in ['6', '7', '8', '9', '10', '11', '12']:
                        item['实发'] = sheet['W' + str(5)].value
                        item['个税'] = sheet['U' + str(5)].value
                        item['养老'] = sheet['P' + str(5)].value
                        item['医疗'] = sheet['Q' + str(5)].value
                        item['公积金'] = sheet['S' + str(5)].value
                else:
                    if year == '2019' and month in ['1']:
                        item['实发'] = sheet['W' + str(5)].value
                        item['个税'] = sheet['U' + str(5)].value
                    else:
                        item['实发'] = sheet['X' + str(5)].value
                        item['个税'] = sheet['V' + str(5)].value
                    # 这几个19年后一样
                    item['养老'] = sheet['P' + str(5)].value
                    item['医疗'] = sheet['Q' + str(5)].value
                    item['公积金'] = sheet['S' + str(5)].value

                dataList.append(item)

        except Exception as err:
            print(err)
    # print('excel数据', dataList)
    # map填充到list, 构建成orgmode表格形式
    # 下边输出的玩意儿copy贴到orgmode， 然后ctrl+c | 搞定
    print('复制下边输出结果到orgmode')
    for item in dataList:
        print(item['时间'], ' ', item['实发'], ' ', item['个税'], ' ', item['养老'], ' ', item['医疗'], ' ', item['公积金'])


if __name__ == '__main__':
    # 第一步：邮箱登录
    server = connect_mail()
    # 第二步：过滤邮箱内容
    # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
    resp, mails, octets = server.list()

    rootPath = '/tmp'
    # print(mails)
    # 倒序遍历邮件
    index = len(mails)
    for i in range(index, 0, -1):
        try:
            # lines存储了邮件的原始文本的每一行
            resp, lines, octets = server.retr(i)
            # 邮件的原始文本, 将bytes格式的消息内容拼接
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            # 解析邮件:
            # """将字符串格式的消息内容转换为email模块支持的格式（<class 'email.message.Message'>）"""
            # 方式1
            # msg = email.message_from_bytes(msg_bytes_content)
            # 方式2
            msg = Parser().parsestr(msg_content)
            From = parseaddr(msg.get('from'))[1]
            To = parseaddr(msg.get('To'))[1]
            # 抄送人
            Cc = parseaddr(msg.get_all('Cc'))[1]
            # 来源hr的, 标题是工资条的
            # 获取消息标题
            subject = decode_str(msg.get('Subject'))
            if '工资条' in subject:
                # 获取附件
                # 第三步：附件下载
                f_list = get_att(msg, savepath=os.path.join(rootPath, str(subject).replace("转发： ", "") + '.rar'))
        except:
            print(i)

    print("文件已下载完成！")

    # 第四步：解压附件并按顺序合并成一个
    dcompress(savepath=rootPath)
    # excel合并归档
    excel_archive(savepath=rootPath)
