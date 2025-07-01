from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# 创建ChatOllama实例，指定模型名称
model = ChatOllama(model="llama3.2:3b")

# 定义你的问题
question = HumanMessage("你是如何工作的？")

# 使用模型处理问题
response = model.invoke([question])

# 打印返回的结果
print(response.content)