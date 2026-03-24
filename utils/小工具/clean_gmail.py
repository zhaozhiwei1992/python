#!/usr/bin/env python3
"""
Gmail 垃圾邮件清理器
自动删除 Reddit、验证码等垃圾邮件
"""

import imaplib
import email
from email.header import decode_header
import re

# Gmail 凭据
USERNAME = 'zhaozhiweishanxi@gmail.com'
PASSWORD = 'rmbk xbda cfkc muzv'
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993


def decode_header_value(header):
    """解码邮件头"""
    if header is None:
        return ''
    decoded = decode_header(header)
    result = ''
    for part, encoding in decoded:
        if isinstance(part, bytes):
            result += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            result += str(part)
    return result


def is_spam_email(from_addr, subject):
    """判断是否为垃圾邮件"""
    from_lower = from_addr.lower()
    subject_lower = subject.lower()

    # 垃圾邮件发件人列表
    spam_senders = [
        'reddit',
        'noreply@',
        'no-reply@',
        'donotreply@',
        'do-not-reply@',
        'notification@',
        'notifications@',
        'alert@',
        'alerts@',
        'newsletter@',
        'newsletters@',
        'digest@',
        'update@',
        'support@',
        'team@',
        'info@',
        'marketing@',
        'promo@',
    ]

    # 垃圾邮件主题关键词
    spam_keywords = [
        'verification code',
        '验证码',
        'your verification',
        'confirm your',
        'verify your',
        'verification',
        'verify',
        'confirm',
        'otp',
        'newsletter',
        'digest',
        'daily digest',
        'weekly digest',
        'update',
        'notification',
        'notifications',
        'welcome to',
        'you\'ve been added',
        'you have been added',
        'invitation',
        'join us',
        'promo',
        'promotion',
        'discount',
        'sale',
        'offer',
        'limited time',
        'exclusive offer',
    ]

    # 检查发件人
    for spam_sender in spam_senders:
        if spam_sender in from_lower:
            return True, f"发件人匹配: {spam_sender}"

    # 检查主题
    for keyword in spam_keywords:
        if keyword in subject_lower:
            return True, f"主题匹配: {keyword}"

    # 检查验证码模式（如：Your code is 123456）
    code_pattern = r'code is \d{4,8}|验证码[:：]\s*\d{4,8}'
    if re.search(code_pattern, subject_lower):
        return True, "验证码匹配"

    return False, None


def scan_and_delete_spam():
    """扫描并删除垃圾邮件"""
    try:
        # 连接到 Gmail IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(USERNAME, PASSWORD)

        # 选择收件箱
        mail.select('INBOX')

        # 搜索所有邮件
        result, data = mail.search(None, 'ALL')
        email_ids = data[0].split()

        print(f"收件箱共有 {len(email_ids)} 封邮件")
        print()
        print("开始扫描垃圾邮件...")
        print()

        spam_count = 0
        spam_emails = []

        # 扫描邮件
        for idx, email_id in enumerate(email_ids):
            try:
                # 获取邮件头
                result, data = mail.fetch(email_id, '(BODY.PEEK[HEADER])')
                raw_header = data[0][1]

                # 解析邮件头
                msg = email.message_from_bytes(raw_header)
                from_addr = decode_header_value(msg.get('From', ''))
                subject = decode_header_value(msg.get('Subject', ''))

                # 判断是否为垃圾邮件
                is_spam, reason = is_spam_email(from_addr, subject)

                if is_spam:
                    spam_count += 1
                    spam_emails.append({
                        'id': email_id,
                        'from': from_addr[:50] + '...' if len(from_addr) > 50 else from_addr,
                        'subject': subject[:50] + '...' if len(subject) > 50 else subject,
                        'reason': reason
                    })

                    # 显示进度
                    if spam_count <= 20:  # 只显示前 20 个
                        print(f"📧 垃圾邮件 {spam_count}:")
                        print(f"   发件人: {from_addr}")
                        print(f"   主题: {subject}")
                        print(f"   原因: {reason}")
                        print()

            except Exception as e:
                continue

        print()
        print("=" * 60)
        print(f"✅ 扫描完成")
        print(f"   总邮件数: {len(email_ids)}")
        print(f"   垃圾邮件: {spam_count}")
        print(f"   垃圾率: {spam_count/len(email_ids)*100:.1f}%")
        print("=" * 60)
        print()

        if spam_count > 0:
            print(f"发现 {spam_count} 封垃圾邮件")
            response = input("是否删除这些垃圾邮件？(y/n): ")

            if response.lower() == 'y':
                print()
                print("开始删除...")

                deleted = 0
                for spam_email in spam_emails:
                    try:
                        mail.store(spam_email['id'], '+FLAGS', '\\Deleted')
                        deleted += 1
                        if deleted % 10 == 0:
                            print(f"已删除: {deleted}/{spam_count}")
                    except Exception as e:
                        print(f"删除邮件 {spam_email['id']} 失败: {e}")

                # 永久删除标记的邮件
                mail.expunge()

                print()
                print(f"✅ 成功删除 {deleted} 封垃圾邮件")
            else:
                print("取消删除")

        # 关闭连接
        mail.close()
        mail.logout()

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("=" * 60)
    print("Gmail 垃圾邮件清理器")
    print("=" * 60)
    print()

    scan_and_delete_spam()
