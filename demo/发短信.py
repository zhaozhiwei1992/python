from twilio.rest import Client


# 使用Twilio的免费手机号发送短信
# 你需要在官网上申请一个账号，这里是官网：https://www.twilio.com/
def send_sms(msg='你好，这是来自你自己的手机测试信息！', my_number="+3l162"):
    # 从官网获得以下信息
    account_sid = 'AC8ef6cdxxxx9873bcad3045a'
    auth_token = '009d3c36xxxxxxbdf73f93'
    twilio_number = '+1804'

    client = Client(account_sid, auth_token)
    try:
        client.messages.create(to=my_number, from_=twilio_number, body=msg)
        print('短信已经发送！')
    except ConnectionError as e:
        print('发送失败，请检查你的账号是否有效或网络是否良好！')
        return e


if __name__ == '__main__':
    send_sms()
# ————————————————
# 版权声明：本文为CSDN博主「查永春」的原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/zyc121561/article/details/78169168
