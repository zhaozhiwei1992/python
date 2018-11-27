import requests
import json
import uuid
import base64


def get_token():
    url = "https://openapi.baidu.com/oauth/2.0/token"
    grant_type = "client_credentials"
    api_key = "dYUhCcuMLgPrDezPa9hNUftK"  # 自己申请的应用
    secret_key = "ssiCyS1PwPB8MiHIP4bAuAHUynGRn54n"  # 自己申请的应用
    data = {'grant_type': grant_type, 'client_id': api_key, 'client_secret': secret_key}
    r = requests.post(url, data=data)
    return json.loads(r.text).get("access_token")


def recognize(sig, rate, token):
    url = "http://vop.baidu.com/server_api"
    speech_length = len(sig)
    speech = base64.b64encode(sig).decode("utf-8")
    mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:]
    rate = rate
    data = {
        "format": "wav",
        "lan": "zh",
        "token": token,
        "len": speech_length,
        "rate": rate,
        "speech": speech,
        "cuid": "14962640",
        "channel": 1,
    }
    data_length = str(len(json.dumps(data).encode("utf-8")))
    headers = {"Content-Type": "application/json",
               "Content-Length": data_length}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print("解析完成----")
    print(r.text)


filename = "two.wav"

signal = open(filename, "rb").read()
rate = 8000

token = get_token()
print("老子的token" + token)
recognize(signal, rate, token)
