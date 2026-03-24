#!/usr/bin/env python3
"""
Gmail 到 Telegram 邮件转发器
使用 IMAP 连接 Gmail，检测新邮件并发送到 Telegram
"""

import imaplib
import email
from email.header import decode_header
import requests
import time
from datetime import datetime
import json
import os

# 配置文件路径
CONFIG_FILE = '/home/zhaozhiwei/clawd/.gmail_forwarder_config.json'
STATE_FILE = '/home/zhaozhiwei/clawd/.gmail_forwarder_state.json'

# Gmail IMAP 配置
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# 代理配置
PROXIES = {
    'http': 'http://10.11.12.164:7890',
    'https': 'http://10.11.12.164:7890',
}


def load_config():
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None


def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_state():
    """加载状态（已处理的邮件）"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'last_uid': 0, 'processed_emails': []}


def save_state(state):
    """保存状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def decode_email_header(header):
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


def format_email_for_telegram(msg):
    """格式化邮件为 Telegram 消息"""
    # 提取邮件信息
    subject = decode_email_header(msg.get('Subject', '无主题'))
    from_addr = decode_email_header(msg.get('From', '未知发件人'))
    date_str = decode_email_header(msg.get('Date', ''))

    # 提取正文
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    continue
                break
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            body = '[无法解码邮件正文]'

    # 限制消息长度（Telegram 限制 4096 字符）
    max_length = 3500
    if len(body) > max_length:
        body = body[:max_length] + '\n\n... (邮件过长，已截断)'

    # 格式化
    message = f"""📧 新邮件

📋 主题: {subject}
👤 发件人: {from_addr}
📅 日期: {date_str}

---
📄 正文:

{body}
"""

    return message


def send_to_telegram(message, bot_token, chat_id):
    """发送消息到 Telegram"""
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        # 使用代理
        response = requests.post(url, data=data, proxies=PROXIES, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"发送到 Telegram 失败: {e}")
        return False


def check_gmail(username, app_password, bot_token, chat_id):
    """检查 Gmail 新邮件"""
    state = load_state()
    last_uid = state.get('last_uid', 0)
    processed = set(state.get('processed_emails', []))

    try:
        # 连接到 Gmail IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(username, app_password)

        # 选择收件箱
        mail.select('INBOX')

        # 搜索所有邮件（按 UID）
        result, data = mail.search(None, 'ALL')
        email_ids = data[0].split()

        print(f"收件箱共有 {len(email_ids)} 封邮件")

        # 查找新邮件（UID > last_uid）
        new_emails = []
        for email_id in email_ids:
            uid = int(email_id)
            if uid > last_uid:
                new_emails.append(uid)

        print(f"发现 {len(new_emails)} 封新邮件")

        # 处理新邮件
        for uid in new_emails:
            if str(uid) in processed:
                continue

            try:
                # 获取邮件
                result, data = mail.fetch(str(uid), '(RFC822)')
                raw_email = data[0][1]

                # 解析邮件
                msg = email.message_from_bytes(raw_email)

                # 格式化并发送到 Telegram
                message = format_email_for_telegram(msg)
                if send_to_telegram(message, bot_token, chat_id):
                    print(f"✅ 已转发邮件 UID: {uid}")
                    processed.add(str(uid))
                else:
                    print(f"❌ 转发失败 UID: {uid}")

            except Exception as e:
                print(f"处理邮件 UID {uid} 时出错: {e}")

        # 更新状态
        if email_ids:
            last_uid = max(int(eid) for eid in email_ids)

        state['last_uid'] = last_uid
        state['processed_emails'] = list(processed)
        save_state(state)

        mail.close()
        mail.logout()

        return len(new_emails)

    except Exception as e:
        print(f"检查 Gmail 时出错: {e}")
        return 0


def main():
    """主函数"""
    print("=" * 60)
    print("Gmail 到 Telegram 邮件转发器")
    print("=" * 60)
    print()

    # 加载配置
    config = load_config()

    if not config:
        print("❌ 未找到配置文件")
        print("请先配置 Gmail 凭据")
        return

    username = config.get('gmail_username')
    app_password = config.get('gmail_app_password')
    bot_token = config.get('telegram_bot_token')
    chat_id = config.get('telegram_chat_id')

    if not username or not app_password:
        print("❌ 配置文件缺少 Gmail 凭据")
        return

    print(f"Gmail: {username}")
    print(f"Telegram Chat ID: {chat_id}")
    print()
    print("开始检查新邮件...")
    print()

    # 检查邮件
    new_count = check_gmail(username, app_password, bot_token, chat_id)

    print()
    print(f"✅ 完成，共处理 {new_count} 封新邮件")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
