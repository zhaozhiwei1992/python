#!/usr/bin/env python3
"""
Gmail 清理超过 7 天的特定邮件
- GitHub 推送邮件（feat、fix 等）
- 新闻邮件
"""

import imaplib
from datetime import datetime, timedelta

# Gmail 凭据
USERNAME = 'zhaozhiweishanxi@gmail.com'
PASSWORD = 'rmbk xbda cfkc muzv'
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993


def delete_old_emails_by_sender(sender_pattern, days):
    """删除超过指定天数、来自特定发件人的邮件"""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(USERNAME, PASSWORD)
        mail.select('INBOX')

        # 计算日期（IMAP 格式：03-Feb-2026）
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')

        # 搜索条件：来自特定发件人且在指定日期之前
        search_criteria = f'(FROM "{sender_pattern}" BEFORE "{cutoff_date}")'
        result, data = mail.search(None, search_criteria)
        email_ids = data[0].split()

        if email_ids:
            # 标记为删除
            for email_id in email_ids:
                mail.store(email_id, '+FLAGS', '\\Deleted')

            # 永久删除
            mail.expunge()

            mail.close()
            mail.logout()
            return len(email_ids)
        else:
            mail.close()
            mail.logout()
            return 0

    except Exception as e:
        print(f"删除 {sender_pattern} 邮件时出错: {e}")
        return 0


def delete_old_emails_by_subject(keyword, days):
    """删除超过指定天数、主题包含特定关键词的邮件"""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(USERNAME, PASSWORD)
        mail.select('INBOX')

        # 计算日期
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')

        # 检查是否包含非 ASCII 字符（如中文）
        try:
            keyword.encode('ascii')
            # 如果是 ASCII，直接使用
            search_criteria = f'(SUBJECT "{keyword}" BEFORE "{cutoff_date}")'
            result, data = mail.search(None, search_criteria)
        except UnicodeEncodeError:
            # 如果包含中文，使用 UTF-8 编码搜索条件
            search_criteria = f'(CHARSET UTF-8 SUBJECT "{keyword}" BEFORE "{cutoff_date}")'
            result, data = mail.search(None, search_criteria.encode('utf-8'))

        email_ids = data[0].split()

        if email_ids:
            # 标记为删除
            for email_id in email_ids:
                mail.store(email_id, '+FLAGS', '\\Deleted')

            # 永久删除
            mail.expunge()

            mail.close()
            mail.logout()
            return len(email_ids)
        else:
            mail.close()
            mail.logout()
            return 0

    except Exception as e:
        print(f"删除主题包含 '{keyword}' 的邮件时出错: {e}")
        return 0


def main():
    """主函数"""
    print("=" * 60)
    print("Gmail 清理超过 7 天的邮件")
    print("=" * 60)
    print()

    # 要删除的 GitHub 邮件
    github_senders = [
        'notifications@github.com',
        'noreply@github.com',
    ]

    # 要删除的新闻邮件关键词（避免空格导致的搜索错误）
    news_keywords = [
        'newsletter',
        '新闻',
        'news',
        'digest',
    ]

    total_deleted = 0
    days = 7

    # 删除 GitHub 邮件
    print("删除超过 7 天的 GitHub 邮件...")
    for sender in github_senders:
        deleted = delete_old_emails_by_sender(sender, days)
        if deleted > 0:
            print(f"  ✅ 删除来自 '{sender}': {deleted} 封")
            total_deleted += deleted

    print()

    # 删除新闻邮件
    print("删除超过 7 天的新闻邮件...")
    for keyword in news_keywords:
        deleted = delete_old_emails_by_subject(keyword, days)
        if deleted > 0:
            print(f"  ✅ 删除主题包含 '{keyword}': {deleted} 封")
            total_deleted += deleted

    print()
    print("=" * 60)
    print(f"✅ 清理完成，共删除 {total_deleted} 封邮件")
    print(f"   日期范围: {days} 天前")
    print("=" * 60)


if __name__ == '__main__':
    main()
