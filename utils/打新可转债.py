# -*- coding: utf8 -*-
from datetime import date, datetime
import requests
from telegram import Bot
from telegram.utils.request import Request
import os

request_params = {
    "headers": {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    },
    "timeout": 10
}


def get_today_bonds():
    r = requests.get("http://data.hexin.cn/ipo/bond/cate/info/",
                     **request_params)
    # 如果不传入参数则为今天
    today = date.today()

    # 今天星期几(星期一 = 1，周日 = 7)
    week_day = date.weekday(today) + 1
    is_work_day_in_week = week_day in range(1, 6)
    # 非工作日不做操作
    if not is_work_day_in_week:
        return

    textList = []
    for bond in r.json():
        print(f"{bond['zqName']}: 申购日期:{bond['sgDate']}")

        currentDate = date.today()
        # sgDate = date.fromisoformat(bond['sgDate'])
        sgDate = datetime.strptime(bond['sgDate'], "%Y-%m-%d").date()
        # 三天内预约
        timedelta = sgDate - currentDate
        if 0 < timedelta.days < 4:
            text = f"""三日内预约打新: {bond['zqName']} 发行量{bond['issue']}亿"""
            # print(text)
            textList.append(text)

        # 当日新债提醒
        if currentDate == sgDate:
            text = f"""今日打新: {bond['zqName']} 发行量{bond['issue']}亿"""
            # print(text)
            # send_msg(text)
            textList.append(text)

    # print("bonds:\n", "\n".join(textList))
    # 钉钉里设置了标签为bonds, 必须传
    if len(textList) > 0:
        return "bonds:\n" + "\n".join(textList)

def send_telegram_message(msg):
    # 替换为你的API令牌
    token = os.environ['TELEGRAM_TOKEN']
    # 替换为你的Telegram账号的ID
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    # 使用带有代理的Session对象创建Bot实例
    # session = requests.Session()
    # session.proxies = {
    #     'http': 'http://127.0.0.1:7890',
    #     'https': 'http://127.0.0.1:7890',
    # }

    """
    python 3.6.15适用
    """
    proxy = Request(proxy_url='http://127.0.0.1:7890')
    bot = Bot(token=token, request=proxy)
    bot.send_message(chat_id=chat_id, text=msg)

def send_ding_talk_message(msg):
    # 设置钉钉 webhook
    webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=" + os.environ["DING_TALK_TOKEN"]

    r = requests.post(webhook_url, json={
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }, **request_params)

if __name__ == '__main__':
    # 获取当天可转债
    msg = get_today_bonds()
    # msg = 'hello world'
    # send_ding_talk_message(msg)
    send_telegram_message(msg)
