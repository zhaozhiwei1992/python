# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: ChatGPT背单词.py
# @Description: 利用chatgpt做一个背单词, 查单词的小工具
# @author zhaozhiwei
# @date 2023/7/27 下午3:22
# @version V1.0

"""
命令测试:

export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export no_proxy="localhost, 127.0.0.1"

curl https://api.openai.com/v1/chat/completions -H "Content-Type: application/json" -H "Authorization: Bearer $OPENAI_API_KEY" -d '{"model": "gpt-3.5-turbo","messages": [{"role": "user", "content": "Say this is a test!"}],"temperature": 0.7}'

接口配额到期就没得完了, 或者花钱

"""

import json
import urllib
import urllib.request
import os

def gpt_completion(api_key, model, prompt, content):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + api_key
    }
    body = {
        'model': model,
        'messages': [
            {
                'role': 'system',
                'content': prompt
            },
            {
                'role': 'user',
                'content': content
            }
        ]
    }
    data = bytes(json.dumps(body), encoding='utf-8')
    req = urllib.request.Request(url, data, headers)
    # with urllib.request.urlopen(req) as resp:
    #     s = resp.read()
    # 创建代理处理器
    proxy_support = urllib.request.ProxyHandler({
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    })

    # 创建使用代理的 opener
    opener = urllib.request.build_opener(proxy_support)

    with opener.open(req) as resp:
        s = resp.read()
    output_json = json.loads(s)
    output_content = output_json['choices'][0]['message']['content']
    if output_content.startswith('```json\n'):
        output_content = output_content[8:len(output_content)-3]
    if output_content.startswith('```\n'):
        output_content = output_content[4:len(output_content)-3]
    return output_content

if __name__ == '__main__':
    api_key = os.environ['OPENAI_API_KEY']
    word = input('English word: ')
    model = 'gpt-4'
    prompt = '你是一个高中英语老师'
    content = f'请给出英文单词"{word}"的音标、英文解释、中文解释，英文填空题、答案和中文翻译，并以如下JSON格式返回：'
    content = content + '''
    ```
    {
        "phonetic": 音标,
        "explain_english": 英文解释,
        "explain_chinese": 中文解释,
        "exam": {
            "question": 英文填空题,
            "answer": 答案,
            "translation": 中文翻译
        }
    }
    ```
    '''
    result = gpt_completion(api_key, model, prompt, content)
    print(result)
