# -*- coding: utf8 -*-
from datetime import date
import requests

request_params = {
    "headers": {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    },
    "timeout": 10
}

# 设置钉钉 webhook
webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=088539a54fcebf90c85a6408f71b919cc404bc3570c9fc4a36cc2f12894bb9e4"

def get_today_bonds():
    r = requests.get("http://data.hexin.cn/ipo/bond/cate/info/",
                     **request_params)

    textList = []
    for bond in r.json():
        print(f"{bond['zqName']}: 申购日期:{bond['sgDate']}")

        currentDate = date.today()
        sgDate = date.fromisoformat(bond['sgDate'])
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
        send_msg("bonds:\n" + "\n".join(textList))

# 发送消息
def send_msg(text):
    r = requests.post(webhook_url, json={
        "msgtype": "text",
        "text": {
            "content": text
        }
    }, **request_params)


if __name__ == '__main__':
    # main_handler("", "") 腾讯云函数的
    get_today_bonds()
