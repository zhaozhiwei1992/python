#!/usr/bin/env python3
import requests

proxies = {
    'http': 'http://10.11.12.164:7890',
    'https': 'http://10.11.12.164:7890',
}

bot_token = '7226653143:AAEjV9eCSoI_5UlFcMnN3cAXF0kwgxfNF-4'
chat_id = '5452583316'

url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

data = {
    'chat_id': chat_id,
    'text': '🧪 测试消息\nGmail Telegram 转发器代理测试成功！',
    'parse_mode': 'Markdown'
}

try:
    response = requests.post(url, data=data, proxies=proxies, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")
