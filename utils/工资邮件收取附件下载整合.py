# !user/bin/python
# _*_ coding: gb2312 _*_
#
# @Title: �����ʼ���ȡ������������.py
# @Description: ���ع�����ϸ�����ϵ�һ��ͳһ��excel����org��
# @author zhaozhiwei
# @date 2023/4/13 ����10:43
# @version V1.0

import email
import os
import poplib
import zipfile
from email.header import decode_header
from email.parser import Parser
from email.utils import parseaddr

# ��ȡexcel
import openpyxl
import rarfile


def decode_str(s):
    """
    # �ַ�����ת��
    """
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def get_att(msg, savepath):
    """
    ���ظ���
    savepath: ֱ��д���ļ���
    """
    attachment_files = []
    for part in msg.walk():
        file_name = part.get_filename()  # ��ȡ������������
        contType = part.get_content_type()
        if file_name:
            h = email.header.Header(file_name)
            # �Ը������ƽ��н���
            dh = email.header.decode_header(h)
            filename = dh[0][0]
            if dh[0][1]:
                filename = decode_str(str(filename, dh[0][1]))  # ���������ƿɶ���
                print("�ʼ��и�������", filename)
                # filename = filename.encode("utf-8")
            data = part.get_payload(decode=True)  # ���ظ���
            # ��ָ��Ŀ¼�´����ļ���ע��������ļ���Ҫ��wbģʽ��
            # ���︽��������subject��, ��������
            # att_file = open(savepath + "\\/" + filename, 'wb')
            att_file = open(savepath, 'wb')
            attachment_files.append(savepath)
            att_file.write(data)  # ���渽��
            att_file.close()
    return attachment_files


def dcompress(savepath):
    """
    ��ȡ���е� ���������������rar�ļ�
    """
    # ������rar��ѹ������
    dcompressPassWord = os.environ['PAY_STUPS_PASSWORD']
    for root, dirs, files in os.walk(savepath):
        try:
            for file in files:
                if "������" not in file:
                    continue
                if ".zip" in os.path.splitext(file)[1]:
                    path = os.path.join(savepath, file)
                    os.chdir(savepath)
                    zip = zipfile.ZipFile(file)  # ����ѹ�ļ�
                    # zip.extractall(src_dir1) # ��ѹָ���ļ�
                    zip.extractall(savepath)
                    zip.close()
                    os.remove(path)
                if ".rar" in os.path.splitext(file)[1]:
                    path = os.path.join(savepath, file)
                    # os.chdir(savepath)
                    rf = rarfile.RarFile(path)
                    # �ڲ��ļ�����ͬ, ���Խ�ѹ��ͬ���ļ���
                    dcompress_path = os.path.join(savepath, os.path.splitext(file)[0])
                    rf.extractall(path=dcompress_path, pwd=dcompressPassWord)
                    # ��ѹָ��·��
                    rf.close()
                    # ��ѹ��ɾ���ļ�
                    # os.remove(path)
        except Exception as err:
            print(err)


def connect_mail():
    """
    ��������
    """
    # ���ӵ�POP3������
    # # POP3���������û���������
    # �˴���������Ȩ��,���ڵ�¼�������ʼ��ͻ���
    password = os.environ['MAIL_126_PASSWORD']
    username = os.environ['MAIL_126_USERNAME']
    host = 'pop3.126.com'
    server = poplib.POP3(host)
    server.user(username)
    # ����������������룬�������poplib.error_proto: b'-ERR login fail'�����ÿ���POP3����ʱ�õ�����Ȩ��
    server.pass_(password)
    # stat()�����ʼ�������ռ�ÿռ�:
    print('Messages: %s. Size: %s' % server.stat())
    return server


def excel_archive(savepath):
    """
    ������excel, ��������, �ϲ�����csv��ʽ����
    """
    dataList = []
    for root, dirs, files in os.walk(savepath):
        try:
            for dir in dirs:
                # ��ȡ���� ������ ���ļ���, ��ȡ��ߵ�xlsx�ļ�
                if "������" not in dir:
                    continue
                # ��ȡÿ��Ŀ¼���ļ� LT-1336_��־ΰ.xlsx
                file_name = os.path.join(root, dir, 'LT-1336_��־ΰ.xlsx')
                wb = openpyxl.load_workbook(file_name)
                sheet = wb.worksheets[0]
                # ��ͬ��ȵ�Ԫ��λ�ò�ͬ, ��Ҫ��������
                # һ�㶼�Ƿ��ڵ�4��
                # dir: xx��x�¹�����
                item = {}
                item['ʱ��'] = str(dir).replace("������", "").replace("��", "-").replace("��", "")
                year = str(item['ʱ��']).split('-')[0]
                month = str(item['ʱ��']).split('-')[1]
                # ���ݲ�ͬ����ļ���ʽ��ͬ���ֱ���, ��ֻ��һ������, ת����map����
                if year in ['2017', '2018']:
                    item['ʵ��'] = sheet['G' + str(4)].value
                    item['��˰'] = sheet['Y' + str(4)].value
                    item['����'] = sheet['R' + str(4)].value
                    item['ҽ��'] = sheet['S' + str(4)].value
                    item['������'] = sheet['U' + str(4)].value
                    if year == '2018' and month in ['6', '7', '8', '9', '10', '11', '12']:
                        item['ʵ��'] = sheet['W' + str(5)].value
                        item['��˰'] = sheet['U' + str(5)].value
                        item['����'] = sheet['P' + str(5)].value
                        item['ҽ��'] = sheet['Q' + str(5)].value
                        item['������'] = sheet['S' + str(5)].value
                else:
                    if year == '2019' and month in ['1']:
                        item['ʵ��'] = sheet['W' + str(5)].value
                        item['��˰'] = sheet['U' + str(5)].value
                    else:
                        item['ʵ��'] = sheet['X' + str(5)].value
                        item['��˰'] = sheet['V' + str(5)].value
                    # �⼸��19���һ��
                    item['����'] = sheet['P' + str(5)].value
                    item['ҽ��'] = sheet['Q' + str(5)].value
                    item['������'] = sheet['S' + str(5)].value

                dataList.append(item)

        except Exception as err:
            print(err)
    # print('excel����', dataList)
    # map��䵽list, ������orgmode�����ʽ
    # �±�����������copy����orgmode�� Ȼ��ctrl+c | �㶨
    print('�����±���������orgmode')
    for item in dataList:
        print(item['ʱ��'], ' ', item['ʵ��'], ' ', item['��˰'], ' ', item['����'], ' ', item['ҽ��'], ' ', item['������'])


if __name__ == '__main__':
    # ��һ���������¼
    server = connect_mail()
    # �ڶ�����������������
    # ���Բ鿴���ص��б�����[b'1 82923', b'2 2184', ...]
    resp, mails, octets = server.list()

    rootPath = '/tmp'
    # print(mails)
    # ��������ʼ�
    index = len(mails)
    for i in range(index, 0, -1):
        try:
            # lines�洢���ʼ���ԭʼ�ı���ÿһ��
            resp, lines, octets = server.retr(i)
            # �ʼ���ԭʼ�ı�, ��bytes��ʽ����Ϣ����ƴ��
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            # �����ʼ�:
            # """���ַ�����ʽ����Ϣ����ת��Ϊemailģ��֧�ֵĸ�ʽ��<class 'email.message.Message'>��"""
            # ��ʽ1
            # msg = email.message_from_bytes(msg_bytes_content)
            # ��ʽ2
            msg = Parser().parsestr(msg_content)
            From = parseaddr(msg.get('from'))[1]
            To = parseaddr(msg.get('To'))[1]
            # ������
            Cc = parseaddr(msg.get_all('Cc'))[1]
            # ��Դhr��, �����ǹ�������
            # ��ȡ��Ϣ����
            subject = decode_str(msg.get('Subject'))
            if '������' in subject:
                # ��ȡ����
                # ����������������
                f_list = get_att(msg, savepath=os.path.join(rootPath, str(subject).replace("ת���� ", "") + '.rar'))
        except:
            print(i)

    print("�ļ���������ɣ�")

    # ���Ĳ�����ѹ��������˳��ϲ���һ��
    dcompress(savepath=rootPath)
    # excel�ϲ��鵵
    excel_archive(savepath=rootPath)
