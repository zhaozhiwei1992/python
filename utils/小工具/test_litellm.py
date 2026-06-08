from openai import OpenAI
import os

client = OpenAI(
    api_key="sk-12345678",
    base_url="http://10.11.12.164:4000/v1"
)

response = client.chat.completions.create(
    model="deepseek-v3",
    messages=[{"role": "user", "content": "你是哪个模型"}]
)
print(response.choices[0].message.content)

