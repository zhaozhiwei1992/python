#!/usr/bin/env python3
import imaplib
import json

username = 'zhaozhiweishanxi@gmail.com'
password = 'rmbk xbda cfkc muzv'
state_file = '/home/zhaozhiwei/clawd/.gmail_forwarder_state.json'

try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    mail.login(username, password)
    mail.select('INBOX')

    # 获取所有邮件 ID
    result, data = mail.search(None, 'ALL')
    email_ids = data[0].split()

    # 获取最大 UID
    max_uid = int(email_ids[-1]) if email_ids else 0

    print(f"收件箱邮件数: {len(email_ids)}")
    print(f"最大 UID: {max_uid}")

    # 保存状态
    state = {
        'last_uid': max_uid,
        'processed_emails': [],
        'init_date': '2026-02-03'
    }

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"✅ 状态已保存到 {state_file}")
    print("从现在开始，只有新邮件才会被转发")

    mail.close()
    mail.logout()

except Exception as e:
    print(f"❌ 错误: {e}")
