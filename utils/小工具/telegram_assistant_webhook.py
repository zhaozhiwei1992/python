"""
个人全能助理，通过telegram不同指令触发完成功能
1. 通过调用dify处理
2. 调用本地服务处理
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simple echo bot using decorators and webhook with fastapi
# It echoes any incoming text messages and does not use the polling method.

import logging
import subprocess

import fastapi
import requests
import uvicorn
import telebot

API_TOKEN = '8157711635:AAG-D7fwvkC8LlMsY41MunQAukDB1sqX_BI'

WEBHOOK_HOST = '19921514.xyz'
WEBHOOK_PORT = 443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_PATH = "assistant"
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

# WEBHOOK_SSL_CERT = './ssl/webhook_cert.pem'  # Path to the ssl certificate
# WEBHOOK_SSL_PRIV = './ssl/webhook_key.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl req -x509 -newkey rsa:4096 -nodes -out webhook_cert.pem -keyout webhook_key.pem -days 365
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://{}:{}/{}/".format(WEBHOOK_HOST, WEBHOOK_PORT, WEBHOOK_PATH)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = fastapi.FastAPI(docs=None, redoc_url=None)


# curl -v -k -X POST http://localhost:8444/assistant/
@app.post(f'/{WEBHOOK_PATH}/')
def process_webhook(update: dict):
    """
    Process webhook calls
    """
    if update:
        update = telebot.types.Update.de_json(update)
        bot.process_new_updates([update])
    else:
        return


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    """
    Handle '/start' and '/help'
    """
    bot.reply_to(message,
                 ("Hi there, I am EchoBot.\n"
                  "I am here to echo your kind words back to you."))


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    """
    Handle all other messages
    """
    bot.reply_to(message, message.text)

# 添加Dify指令处理器
@bot.message_handler(commands=['send'])
def handle_dify_command(message):
    prompt = message.text.split(" ", 1)[1]  # 提取指令后的文本
    response = call_dify_api(prompt)  # 调用Dify API
    bot.reply_to(message, response)

# 添加本地服务指令处理器
@bot.message_handler(commands=['local'])
def handle_local_command(message):
    cmd = message.text.split(" ", 1)[1]
    result = subprocess.run(cmd, shell=True, capture_output=True)
    bot.reply_to(message, result.stdout.decode())


# Remove webhook, it fails sometimes the set if there is a previous webhook
# bot.remove_webhook()

# Set webhook
bot.set_webhook(
    url=WEBHOOK_URL_BASE,
    # 如果需要全部用自签名证书再放开
    # certificate=open(WEBHOOK_SSL_CERT, 'r')
)

# 本地服务启动地址，本地用http就够了，如果设置了ssl,自动会用https
uvicorn.run(
    app,
    host='0.0.0.0',
    port=8444,
    # ssl_certfile=WEBHOOK_SSL_CERT,
    # ssl_keyfile=WEBHOOK_SSL_PRIV
)

def call_dify_api(prompt):
    headers = {"Authorization": "Bearer DIFY_API_KEY"}
    data = {"inputs": {"query": prompt}}
    response = requests.post(
        "https://api.dify.ai/v1/workflows/{id}/run",
        json=data, headers=headers
    )
    return response.json()["output"]

# 安全执行本地命令
def safe_local_exec(cmd):
    allowed_commands = ["数据分析", "文件清洗"]  # 预定义白名单
    if cmd not in allowed_commands:
        return "指令未授权"
    return subprocess.run(
        f"/opt/scripts/{cmd}.sh",
        shell=True,
        timeout=30
    ).stdout.decode()